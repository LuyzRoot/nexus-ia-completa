from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    provider: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    tokens_used: int

class ConversationSchema(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    messages: List[MessageSchema]
    
    class Config:
        from_attributes = True