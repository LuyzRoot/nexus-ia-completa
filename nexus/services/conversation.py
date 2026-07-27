from nexus.services.base import BaseService
from nexus.models.conversation import Conversation, Message
from database.session import AsyncSessionLocal
from sqlalchemy.future import select

class ConversationService(BaseService):
    """Conversation business logic"""
    
    async def initialize(self):
        pass
    
    async def shutdown(self):
        pass
    
    async def create_conversation(self, user_id: str, title: str = None):
        async with AsyncSessionLocal() as db:
            conversation = Conversation(user_id=user_id, title=title)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            return conversation
    
    async def get_conversation(self, conversation_id: str, user_id: str):
        async with AsyncSessionLocal() as db:
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
    
    async def add_message(self, conversation_id: str, role: str, content: str):
        async with AsyncSessionLocal() as db:
            message = Message(conversation_id=conversation_id, role=role, content=content)
            db.add(message)
            await db.commit()
            await db.refresh(message)
            return message
