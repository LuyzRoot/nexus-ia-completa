# app/api/conversations.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User as UserModel, Conversation, Message
from app.schemas import ConversationCreate, ConversationOut, MessageOut
from app.agents import registry, manager as agent_manager

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("/agents")
def get_agents():
    return registry.list_agents()


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    agent_type = payload.agent_type if payload.agent_type in [a["id"] for a in registry.list_agents()] else "assistant"
    conversation = Conversation(user_id=current_user.id, title=payload.title, agent_type=agent_type)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("", response_model=List[ConversationOut])
def list_conversations(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_messages(conversation_id: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta conversa")
    return conversation.messages