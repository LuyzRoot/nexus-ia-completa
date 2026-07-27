"""
Auth HTTP endpoints (router).

Endpoints:
- POST /api/v1/auth/register  -> cria usuário (retorna UserOut)
- POST /api/v1/auth/login     -> OAuth2 password flow (form), retorna Token
- GET  /api/v1/auth/me        -> retorna o usuário atual (requires auth)

Observação:
- Este módulo usa app.config.security.create_access_token and app.config.security.verify_password/get_password_hash.
- Se já existir um módulo de auth em app/api/auth.py você pode optar por usar apenas as dependências (app.auth.deps) e remover endpoints duplicados.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as UserModel
from app.auth import schemas
from app.config.security import get_password_hash, verify_password, create_access_token
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
    user = UserModel(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário desativado")
    token = create_access_token(subject=user.id, extra_claims={"role": getattr(user.role, "value", str(user.role))})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: UserModel = Depends(get_current_user)):
    return current_user