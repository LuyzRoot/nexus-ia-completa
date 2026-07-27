"""
Webhook do WhatsApp (Meta Cloud API) — canal de comandos por voz/texto.

Segurança em duas camadas, ambas obrigatórias:
1. Assinatura do webhook (X-Hub-Signature-256) — garante que a requisição
   veio mesmo da Meta.
2. Allowlist de números (WHATSAPP_ALLOWED_NUMBERS) — garante que só quem
   você autorizou consegue falar com o assistente. Sem isso, qualquer pessoa
   que descobrisse seu número de WhatsApp Business viraria "usuário".

O processamento roda em BackgroundTask: a Meta exige resposta 200 rápida no
webhook (ela reenvia se demorar/der erro), então confirmamos o recebimento
na hora e processamos a mensagem depois, em segundo plano.
"""
import logging
import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import User, Conversation, Message, MessageRole, WhatsAppLink
from app.security import hash_password
from app.services import whatsapp
from app.services.stt import transcribe_audio, STTServiceError
from app.services.voice import synthesize_speech, VoiceServiceError, is_voice_configured
from app.services.orchestrator import orchestrator
from app.services.skills import SKILL_DEFINITIONS, execute_skill
from app.routers.chat import _build_messages, _parse_structured_reply

logger = logging.getLogger("nexus.whatsapp.router")

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Handshake de configuração do webhook no painel da Meta (chamado uma vez, manualmente, por você)."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN and settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge or "", media_type="text/plain")
    return Response(status_code=status.HTTP_403_FORBIDDEN)


def _get_or_create_link(db: Session, phone_number: str) -> WhatsAppLink:
    link = db.query(WhatsAppLink).filter(WhatsAppLink.phone_number == phone_number).first()
    if link:
        return link

    user = User(
        email=f"whatsapp+{phone_number}@nexus.local",
        hashed_password=hash_password(secrets.token_urlsafe(32)),
        full_name=f"WhatsApp {phone_number}",
    )
    db.add(user)
    db.flush()  # garante user.id antes de usar como FK

    conversation = Conversation(user_id=user.id, title="WhatsApp", agent_type="executive")
    db.add(conversation)
    db.flush()

    link = WhatsAppLink(phone_number=phone_number, user_id=user.id, conversation_id=conversation.id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


async def _process_incoming(from_number: str, msg: dict, db_dependency) -> None:
    """
    Roda em background: transcreve (se áudio), chama o pipeline de chat, responde no WhatsApp.
    Recebe `db_dependency` (resolvido de request.app.dependency_overrides, igual ao streaming
    do chat) em vez de importar SessionLocal fixo, pra respeitar o banco de teste nos testes.
    """
    db_gen = db_dependency()
    db = next(db_gen)
    try:
        link = _get_or_create_link(db, from_number)
        conversation = db.query(Conversation).filter(Conversation.id == link.conversation_id).first()

        reply_with_voice = False
        if msg["type"] == "text":
            user_text = msg["text"]
        elif msg["type"] == "audio":
            try:
                audio_bytes, content_type = await whatsapp.download_media(msg["media_id"])
                stt_result = await transcribe_audio(audio_bytes, content_type=content_type)
                user_text = stt_result["text"]
            except STTServiceError as exc:
                logger.error("Falha na transcrição do áudio do WhatsApp: %s", exc)
                await whatsapp.send_text_message(
                    from_number, "Não consegui entender o áudio agora. Pode tentar de novo ou mandar em texto?"
                )
                return
            if not user_text.strip():
                await whatsapp.send_text_message(from_number, "Não entendi nada no áudio — pode repetir?")
                return
            reply_with_voice = settings.WHATSAPP_REPLY_WITH_VOICE
        else:
            await whatsapp.send_text_message(from_number, "Por enquanto só entendo texto e áudio por aqui.")
            return

        user_msg = Message(conversation_id=conversation.id, role=MessageRole.user, content=user_text)
        db.add(user_msg)
        db.commit()

        messages = _build_messages(db, conversation, link.user_id)

        async def skill_executor(tool_name: str, tool_input: dict) -> dict:
            return await execute_skill(tool_name, tool_input, db, link.user_id)

        try:
            result = await orchestrator.complete_with_tools(
                messages, tools=SKILL_DEFINITIONS, executor=skill_executor
            )
        except RuntimeError as exc:
            logger.error("Orquestrador falhou no canal WhatsApp: %s", exc)
            await whatsapp.send_text_message(from_number, "Meu backend de IA está indisponível agora, tenta em instantes.")
            return

        structured = _parse_structured_reply(result.text)
        reply_text = structured["reply"]

        db.add(
            Message(
                conversation_id=conversation.id,
                role=MessageRole.assistant,
                content=reply_text,
                provider_used=result.provider_name,
            )
        )
        db.commit()

        await whatsapp.send_text_message(from_number, reply_text)

        if reply_with_voice and await is_voice_configured():
            try:
                audio_bytes = await synthesize_speech(reply_text)
                await whatsapp.send_audio_message(from_number, audio_bytes)
            except VoiceServiceError as exc:
                logger.warning("TTS falhou no canal WhatsApp (respondi só em texto): %s", exc)
    except Exception:
        logger.exception("Erro inesperado processando mensagem do WhatsApp")
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    if not whatsapp.verify_signature(raw_body, signature):
        logger.warning("Webhook do WhatsApp com assinatura inválida — recusado")
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    payload = await request.json()
    msg = whatsapp.extract_incoming_message(payload)
    if msg is None:
        return {"status": "ignored"}  # ex: recibo de entrega/leitura, não é mensagem nova

    from_number = msg["from"]
    if not whatsapp.is_number_allowed(from_number):
        logger.warning("Mensagem de número não autorizado recusada: %s", from_number)
        return {"status": "ignored"}

    db_dependency = request.app.dependency_overrides.get(get_db, get_db)
    background_tasks.add_task(_process_incoming, from_number, msg, db_dependency)
    return {"status": "received"}
