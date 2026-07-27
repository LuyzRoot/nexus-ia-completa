"""
Short-term memory: last N messages of a conversation, formatting for LLM.
Provides:
- get_short_term_context(db, conversation_id, max_messages=20)
- append_message(db, conversation_id, role, content)
- prune_conversation_if_needed(db, conversation_id, max_messages=200)  # optional trimming/summarization
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Message, MessageRole  # assumes models.Message exists
import logging

logger = logging.getLogger("memory.short_term")


def get_short_term_context(db: Session, conversation_id: str, max_messages: int = 20) -> List[Dict[str, str]]:
    """
    Return the last up to `max_messages` messages for the conversation
    in the format expected by LLM orchestrator: [{"role": "user"|"assistant"|"system", "content": "..."}].
    """
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
        .all()
    )
    # messages come newest-first; reverse to chronological order
    msgs.reverse()
    return [{"role": m.role.value if hasattr(m.role, "value") else m.role, "content": m.content} for m in msgs]


def append_message(db: Session, conversation_id: str, role: str, content: str) -> Message:
    """
    Append a message to the conversation (persist).
    role can be "user" | "assistant" | "system"
    Returns the Message ORM object.
    """
    if role not in ("user", "assistant", "system"):
        # allow Enum or string but prefer validation by caller
        role_enum = MessageRole.user if role == "user" else MessageRole.assistant
    else:
        role_enum = MessageRole(role) if hasattr(MessageRole, role) else role

    msg = Message(conversation_id=conversation_id, role=role_enum, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def prune_conversation_if_needed(db: Session, conversation_id: str, max_messages: int = 500, summarizer=None) -> Optional[str]:
    """
    If conversation has more than max_messages, optionally summarize older messages and replace them
    by a single assistant/system message that contains the summary. Returns summary text or None.

    - summarizer: optional callable(messages: List[dict]) -> str. If None, no summarization done.
    """
    count = db.query(Message).filter(Message.conversation_id == conversation_id).count()
    if count <= max_messages:
        return None

    if summarizer is None:
        logger.info("prune_conversation_if_needed: conversation too long but no summarizer provided; skipping summarization.")
        return None

    # fetch all messages, produce summary for the oldest chunk
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    # create a window to summarize: oldest half of messages
    cutoff = max(1, len(messages) // 2)
    to_summarize = messages[:cutoff]
    text = "\n".join([f"{m.role.value if hasattr(m.role,'value') else m.role}: {m.content}" for m in to_summarize])
    try:
        summary = summarizer(text)
    except Exception as exc:
        logger.exception("Error while summarizing conversation: %s", exc)
        return None

    # delete summarized messages and insert a system message with the summary
    try:
        for m in to_summarize:
            db.delete(m)
        db.commit()
        from app.models import Message as MsgModel, MessageRole as MsgRole
        summary_msg = MsgModel(conversation_id=conversation_id, role=MsgRole.system, content=f"[Resumo automático anterior]: {summary}")
        db.add(summary_msg)
        db.commit()
    except Exception as exc:
        logger.exception("Failed replacing summarized messages: %s", exc)
        db.rollback()
        return None

    return summary