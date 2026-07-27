"""
Long-term memory: persistent key/value memory per user (MemoryEntry model).
Provides:
- get_long_term_memory(db, user_id) -> Dict[str,str]
- upsert_memory(db, user_id, key, value) -> MemoryEntry
- list_memory_keys(db, user_id)
- delete_memory(db, user_id, key)
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models import MemoryEntry
import logging

logger = logging.getLogger("memory.long_term")


def get_long_term_memory(db: Session, user_id: str) -> Dict[str, str]:
    """
    Return dict of key -> value for the user's long-term memory.
    """
    entries = db.query(MemoryEntry).filter(MemoryEntry.user_id == user_id).all()
    return {e.key: e.value for e in entries}


def upsert_memory(db: Session, user_id: str, key: str, value: str) -> MemoryEntry:
    """
    Insert or update a memory entry for the user.
    """
    entry = db.query(MemoryEntry).filter(MemoryEntry.user_id == user_id, MemoryEntry.key == key).first()
    if entry:
        entry.value = value
    else:
        entry = MemoryEntry(user_id=user_id, key=key, value=value)
        db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_memory_keys(db: Session, user_id: str) -> List[str]:
    rows = db.query(MemoryEntry.key).filter(MemoryEntry.user_id == user_id).all()
    return [r[0] for r in rows]


def delete_memory(db: Session, user_id: str, key: str) -> bool:
    entry = db.query(MemoryEntry).filter(MemoryEntry.user_id == user_id, MemoryEntry.key == key).first()
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True