import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.limiter import limiter
from app.routers import auth, users, conversations, chat, memory, voice, reminders, todos, whatsapp, home_assistant

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend MVP do NEXUS SYSTEM AI — API Gateway, Auth, Model Orchestrator, Agentes, Memória.",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(status_code=429, content={"detail": "Limite de requisições excedido"}),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(voice.router)
app.include_router(reminders.router)
app.include_router(todos.router)
app.include_router(whatsapp.router)
app.include_router(home_assistant.router)


@app.on_event("startup")
def on_startup():
    # MVP: cria as tabelas diretamente. Em produção, use Alembic (ver README/roadmap).
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}
