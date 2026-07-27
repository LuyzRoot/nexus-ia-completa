# app/api/whatsapp.py
import hmac
import hashlib
import json
import time
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict

from app.config.settings import settings
from app.services.whatsapp import verify_signature, extract_incoming_message, is_number_allowed, send_text_message

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
def verify(hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    # Meta verification handshake
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def webhook(req: Request, background_tasks: BackgroundTasks):
    raw = await req.body()
    sig = req.headers.get("x-hub-signature-256", "")
    if not verify_signature(raw, sig):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = json.loads(raw)
    msg = extract_incoming_message(payload)
    if msg is None:
        return {"status": "ignored"}

    from_number = msg["from"]
    if not is_number_allowed(from_number):
        return {"status": "ignored"}

    # process message in background
    async def _process():
        if msg["type"] == "text":
            text = msg["text"]
            # Here you should route to your conversation pipeline; for MVP, reply with a mock
            reply = f"Recebido: {text}"
            await send_text_message(from_number, reply)
        else:
            await send_text_message(from_number, "Tipo de mensagem não suportado no momento.")

    background_tasks.add_task(_process)
    return {"status": "received"}