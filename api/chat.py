# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.schemas import ChatRequest, ChatResponse
from app.models import User as UserModel, Conversation, Message, MessageRole
from app.memory import get_short_term_context, get_long_term_memory, build_context_block
from app.agents.registry import get_agent
from app.services.orchestrator import orchestrator

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # validate conversation ownership
    conv = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada ou sem acesso")

    # persist user message
    user_msg = Message(conversation_id=conv.id, role=MessageRole.user, content=payload.message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Build messages for orchestrator: system message from agent + short-term + long-term
    agent = get_agent(conv.agent_type)
    long_term = get_long_term_memory(db, current_user.id)
    system_block = agent.to_system_role(long_term_memory=long_term) if agent else {"role": "system", "content": build_context_block(long_term)}
    short_term = get_short_term_context(db, conv.id)

    messages = [system_block] + short_term + [{"role": "user", "content": payload.message}]

    # Use orchestrator to get response
    try:
        provider_resp = await orchestrator.complete(messages)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # persist assistant message
    assistant_msg = Message(conversation_id=conv.id, role=MessageRole.assistant, content=provider_resp.text, provider_used=provider_resp.provider_name)
    db.add(assistant_msg)
    db.commit()

    # return {"conversation_id": conv.id, "reply": provider_resp.text, "provider_used": provider_resp.provider_name, "panel": None, "skills_used": getattr(provider_resp, "tools_used", [])}