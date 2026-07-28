from fastapi import FastAPI
import logging

from config.logging import configure_logging
from core.registry import Registry

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="NEXUS IA (refactor)")
registry = Registry()
registry.discover_all()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "nexus-ia", "discovered": registry.summary()}

@app.get("/")
async def root():
    return {"message": "NEXUS IA API (refactor)", "docs": "/docs"}
