from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models import User, MemoryEntry
from app.schemas import MemoryUpsert, MemoryOut
from app.services.memory import upsert_memory

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.put("", response_model=MemoryOut)
def set_memory(
    payload: MemoryUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = upsert_memory(db, current_user.id, payload.key, payload.value)
    return entry


@router.get("", response_model=List[MemoryOut])
def list_memory(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MemoryEntry).filter(MemoryEntry.user_id == current_user.id).all()
