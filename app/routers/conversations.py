from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Conversation, Message
from app.schemas import ConversationCreate, ConversationOut, MessageOut
from app.services.agents import AGENT_PROFILES, DEFAULT_AGENT, list_agents

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("/agents")
def get_agents():
    return list_agents()


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent_type = payload.agent_type if payload.agent_type in AGENT_PROFILES else DEFAULT_AGENT
    conversation = Conversation(user_id=current_user.id, title=payload.title, agent_type=agent_type)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("", response_model=List[ConversationOut])
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _get_owned_conversation(db, conversation_id, current_user.id)
    return conversation.messages


def _get_owned_conversation(db: Session, conversation_id: str, user_id: str) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
    if conversation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta conversa")
    return conversation
