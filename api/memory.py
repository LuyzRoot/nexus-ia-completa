# app/api/memory.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import MemoryEntry, User as UserModel
from app.schemas import MemoryUpsert, MemoryOut
from app.memory import upsert_memory, get_long_term_memory

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.put("", response_model=MemoryOut)
def upsert(payload: MemoryUpsert, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    entry = upsert_memory(db, current_user.id, payload.key, payload.value)
    return entry


@router.get("", response_model=List[MemoryOut])
def list_memory(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    entries = db.query(MemoryEntry).filter(MemoryEntry.user_id == current_user.id).order_by(MemoryEntry.updated_at.desc()).all()
    return entries