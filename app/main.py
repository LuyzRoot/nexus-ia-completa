from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.auth.routes import router as auth_router
from api.chat.routes import router as chat_router

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

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "nexus-ia", "version": "2.0.0"}

@app.get("/")
async def root():
    return {"message": "NEXUS IA API v2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)