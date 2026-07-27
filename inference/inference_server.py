"""
FastAPI entrypoint for inference service.
Include this module from your main app or run standalone:
  uvicorn inference.server:app --reload --port 8001
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from inference.routes import router as inference_router
from app.config.logging import configure_logging
from app.config.settings import settings

configure_logging()
logger = logging.getLogger("inference.server")

app = FastAPI(title="NEXUS Inference", version="0.1.0")

# CORS — mirror app settings
origins = getattr(settings, "CORS_ORIGINS", ["*"])
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(inference_router, prefix="/inference", tags=["inference"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "inference"}