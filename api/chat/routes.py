from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.schemas import ChatRequest, ChatResponse
from api.auth.security import get_current_user
from core.llm.router import get_llm_router
from models.conversation import Conversation, Message
from database.session import get_db

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = user_data["user_id"]
    llm_router = get_llm_router()
    
    if request.conversation_id:
        stmt = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user_id, title=request.message[:50])
        db.add(conversation)
        await db.flush()
    
    stmt = select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)
    result = await db.execute(stmt)
    messages_history = result.scalars().all()
    
    messages = [{"role": msg.role, "content": msg.content} for msg in messages_history]
    messages.append({"role": "user", "content": request.message})
    
    try:
        response_text = await llm_router.chat(messages=messages, provider=request.provider, temperature=0.7, max_tokens=1024)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
    
    user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
    assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=response_text)
    
    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()
    
    return ChatResponse(conversation_id=conversation.id, message_id=assistant_msg.id, response=response_text, tokens_used=0)

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = user_data["user_id"]
    stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    stmt = select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
    }

@router.get("/")
async def list_conversations(user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = user_data["user_id"]
    stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in conversations]