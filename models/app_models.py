"""
ORM models usados pelo NEXUS app.

- Tenta reutilizar `Base` de app.database se disponível; senão cria um declarative_base local.
- Usa tipos compatíveis com Postgres (UUID/text/JSON) de modo portátil.
- Inclui modelos: User, Conversation, Message, MemoryEntry, Reminder, Todo, AuditLog,
  AgentProfile, PendingAction.
- Use alembic para migrações em produção. Este arquivo é um ponto único para modelos referenciados em outros módulos.
"""
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Text,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base

# Try to reuse Base from app.database if exists (so app.main.create_all() will work with same Base)
try:
    from app.database import Base  # type: ignore
    _HAS_EXTERNAL_BASE = True
except Exception:
    Base = declarative_base()
    _HAS_EXTERNAL_BASE = False


def _new_uuid_hex():
    return uuid.uuid4().hex


def utcnow():
    return datetime.utcnow()


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"
    service = "service"


class MessageRole(enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


# Helper for UUID column that works with Postgres and SQLite
def UUIDColumn(name=None, primary_key=False, default=None, nullable=False):
    # prefer Postgres UUID type when available
    try:
        # If PG dialect present import will succeed; column type PG_UUID kept
        return Column(PG_UUID(as_uuid=False), name=name, primary_key=primary_key, default=default, nullable=nullable)
    except Exception:
        # fallback to simple String
        return Column(String(36), name=name, primary_key=primary_key, default=default, nullable=nullable)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(512), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("MemoryEntry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role.value}>"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=True)
    agent_type = Column(String(100), nullable=True, index=True)  # e.g., "assistant", "coder"
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation id={self.id} user_id={self.user_id} agent={self.agent_type}>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    provider_used = Column(String(200), nullable=True)  # which LLM/provider produced assistant content
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message id={self.id} conversation_id={self.conversation_id} role={self.role.value} created_at={self.created_at}>"


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="memories")

    def __repr__(self):
        return f"<MemoryEntry id={self.id} user_id={self.user_id} key={self.key}>"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    remind_at = Column(DateTime(timezone=True), nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    notified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Reminder id={self.id} user_id={self.user_id} remind_at={self.remind_at} done={self.done}>"


class Todo(Base):
    __tablename__ = "todos"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Todo id={self.id} user_id={self.user_id} done={self.done}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(200), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AuditLog id={self.id} user_id={self.user_id} action={self.action}>"


# Agent profiles and pending actions: these overlap with database/agent_models.py example.
# We include here for convenience and single-source-of-truth; if you already have db/agent_models,
# you can remove duplicates or import from there.
class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    id = Column(String(100), primary_key=True)  # e.g., "assistant", "coder.custom"
    spec = Column(JSONB, nullable=False)
    owner = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AgentProfile id={self.id} owner={self.owner} active={self.is_active}>"


class PendingAction(Base):
    __tablename__ = "pending_actions"
    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    agent_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    conversation_id = Column(String(100), nullable=True)
    action_payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved = Column(Boolean, default=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    processed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<PendingAction id={self.id} agent_id={self.agent_id} user_id={self.user_id} approved={self.approved}>"