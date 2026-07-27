"""
Conversation helpers: summarization, storing conversation-level summaries (as MemoryEntry), etc.
- summarize_conversation(db, conversation_id, summarizer_callable)
- get_conversation_summary(db, conversation_id)
- set_conversation_summary(db, conversation_id, text)
"""
from typing import Optional, Callable
from sqlalchemy.orm import Session
from app.models import Message, MemoryEntry
import logging

logger = logging.getLogger("memory.conversation")


def _gather_messages_text(db: Session, conversation_id: str, limit: int = 10000) -> str:
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .all()
    )
    text_parts = []
    for m in msgs:
        role = m.role.value if hasattr(m.role, "value") else str(m.role)
        text_parts.append(f"{role}: {m.content}")
    return "\n".join(text_parts)


def summarize_conversation(db: Session, conversation_id: str, summarizer: Callable[[str], str]) -> Optional[str]:
    """
    Create a summary for the conversation using the provided summarizer callable.
    Stores the summary in MemoryEntry under key "conversation_summary:{conversation_id}" and returns it.
    """
    text = _gather_messages_text(db, conversation_id)
    if not text.strip():
        return None
    try:
        summary = summarizer(text)
    except Exception as exc:
        logger.exception("summarize_conversation failed: %s", exc)
        return None

    key = f"conversation_summary:{conversation_id}"
    entry = db.query(MemoryEntry).filter(MemoryEntry.user_id == None, MemoryEntry.key == key).first()  # global summary (no user)
    if entry:
        entry.value = summary
    else:
        entry = MemoryEntry(user_id=None, key=key, value=summary)
        db.add(entry)
    db.commit()
    return summary


def get_conversation_summary(db: Session, conversation_id: str) -> Optional[str]:
    key = f"conversation_summary:{conversation_id}"
    entry = db.query(MemoryEntry).filter(MemoryEntry.user_id == None, MemoryEntry.key == key).first()
    return entry.value if entry else None


def set_conversation_summary(db: Session, conversation_id: str, text: str):
    key = f"conversation_summary:{conversation_id}"
    entry = db.query(MemoryEntry).filter(MemoryEntry.user_id == None, MemoryEntry.key == key).first()
    if entry:
        entry.value = text
    else:
        entry = MemoryEntry(user_id=None, key=key, value=text)
        db.add(entry)
    db.commit()
    return entry