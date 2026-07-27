from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user
from app.models import User
from app.services import home_assistant as ha

router = APIRouter(prefix="/api/v1/home-assistant", tags=["home-assistant"])


@router.get("/status")
async def ha_status(current_user: User = Depends(get_current_user)):
    return {"configured": ha.is_ha_configured()}


@router.get("/devices")
async def ha_devices(domain: str | None = None, current_user: User = Depends(get_current_user)):
    if not ha.is_ha_configured():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Home Assistant não configurado")
    try:
        return {"devices": await ha.list_states(domain)}
    except ha.HomeAssistantError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
