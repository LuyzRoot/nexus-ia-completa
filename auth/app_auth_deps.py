"""
Auth dependencies for FastAPI endpoints.

- oauth2_scheme: OAuth2PasswordBearer pointing to the login endpoint.
- get_current_user: validates jwt token and returns User ORM object.
- require_admin: dependency that raises 403 if user is not admin.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.config.security import decode_access_token
from app.database import get_db
from app.models import User as UserModel, UserRole
from app.auth import schemas

# This should match the login endpoint path you include in the app.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # adjust if your login path differs


def _get_payload_from_token(token: str) -> Optional[dict]:
    """
    Uses app.config.security.decode_access_token to decode and validate the token.
    Returns payload dict or None.
    """
    try:
        payload = decode_access_token(token)
        return payload
    except Exception:
        return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    payload = _get_payload_from_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
    return user


def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    try:
        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão de administrador necessária")
    except Exception:
        # If role stored as string, compare value
        if getattr(current_user, "role", None) not in (UserRole.admin, UserRole.admin.value, "admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão de administrador necessária")
    return current_user