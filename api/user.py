# app/api/users.py
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import User as UserModel
from app.schemas import UserOut

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), admin: UserModel = Depends(require_admin)):
    users = db.query(UserModel).order_by(UserModel.created_at.desc()).all()
    return users