import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, DateTime, Boolean, ForeignKey, Text, Enum, Integer, UniqueConstraint
)

from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("MemoryEntry", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String, default="Nova conversa")
    agent_type = Column(String, default="executive")  # ex: executive, research, coding
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation",
        cascade="all, delete-orphan", order_by="Message.created_at"
    )


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    provider_used = Column(String, nullable=True)  # qual provedor de IA respondeu (auditoria)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class MemoryEntry(Base):
    """
    Memória de longo prazo, simples (chave/valor por usuário).
    Placeholder para evolução futura com banco vetorial (pgvector/Qdrant) — ver README.
    """
    __tablename__ = "memory_entries"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_memory_key"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="memories")


class AuditLog(Base):
    """Registro imutável de ações sensíveis (login, chamadas de modelo, alterações de RBAC)."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Reminder(Base):
    """Lembrete criado pelo usuário — via conversa (skill) ou API direta."""
    __tablename__ = "reminders"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    remind_at = Column(DateTime(timezone=True), nullable=False)
    done = Column(Boolean, default=False)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class WhatsAppLink(Base):
    """
    Vincula um número de WhatsApp (wa_id, formato E.164 sem '+') a um usuário
    interno e a uma conversa fixa — assim o histórico e a memória de longo
    prazo do canal WhatsApp são os mesmos de um usuário normal do app.
    Criado automaticamente no primeiro contato de um número permitido
    (ver WHATSAPP_ALLOWED_NUMBERS); nunca por auto-cadastro aberto.
    """
    __tablename__ = "whatsapp_links"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Todo(Base):
    """Item de lista de tarefas do usuário."""
    __tablename__ = "todos"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
