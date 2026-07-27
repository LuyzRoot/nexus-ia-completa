# NEXUS Main Application v2.0
__version__ = "2.0.0"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(
    title="NEXUS IA v2.0",
    description="Plataforma completa de IA com multi-provedores e multimodal",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Import routes
from api.auth.routes import router as auth_router
from api.chat.routes import router as chat_router
from nexus.pages.nexus_skills import router as skills_router
from nexus.pages.nexus_apis import router as apis_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(skills_router)
app.include_router(apis_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "nexus-ia", "version": "2.0.0"}

@app.get("/")
async def root():
    return {"message": "NEXUS IA API v2.0.0", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("nexus.nexus_main:app", host="0.0.0.0", port=8000, reload=True)