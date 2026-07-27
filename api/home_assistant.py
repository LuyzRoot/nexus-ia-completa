# app/api/home_assistant.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.database import get_db
from app.services import home_assistant as ha_service

router = APIRouter(prefix="/api/v1/home-assistant", tags=["home_assistant"])


@router.get("/status")
def status(current_user=Depends(get_current_user)):
    return {"configured": ha_service.is_ha_configured()}


@router.get("/devices")
async def list_devices(domain: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not ha_service.is_ha_configured():
        raise HTTPException(status_code=503, detail="Home Assistant not configured")
    try:
        entities = await ha_service.list_states(domain_filter=domain)
    except ha_service.HomeAssistantError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"devices": [{"name": e["friendly_name"], "state": e["state"]} for e in entities]}