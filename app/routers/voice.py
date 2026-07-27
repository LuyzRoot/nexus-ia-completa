from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.deps import get_current_user
from app.models import User
from app.services.voice import synthesize_speech, VoiceNotConfiguredError, VoiceServiceError
from app.services.stt import transcribe_audio, STTNotConfiguredError, STTServiceError
from app.limiter import limiter

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice_id: str | None = None


@router.post("/speak")
@limiter.limit("30/minute")
async def speak(
    request: Request,
    payload: SpeakRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Retorna o áudio (MP3) da fala sintetizada. O cliente toca direto:
    `new Audio(URL.createObjectURL(blob)).play()`.
    """
    try:
        audio_bytes = await synthesize_speech(payload.text, voice_id=payload.voice_id)
    except VoiceNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice Engine não configurado (ELEVENLABS_API_KEY ausente) — use fallback do navegador",
        )
    except VoiceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return Response(content=audio_bytes, media_type="audio/mpeg")


@router.post("/transcribe")
@limiter.limit("30/minute")
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    language: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """
    Recebe um arquivo de áudio (webm/wav/mp3) e retorna a transcrição.
    Sem `language`, o Deepgram tenta detectar o idioma automaticamente —
    é assim que a entrada por voz vira multi-idioma de verdade (o
    reconhecimento do navegador exige fixar o idioma antes de falar).
    """
    audio_bytes = await file.read()
    try:
        result = await transcribe_audio(
            audio_bytes, content_type=file.content_type or "audio/webm", language=language
        )
    except STTNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STT não configurado (DEEPGRAM_API_KEY ausente) — use o reconhecimento do navegador",
        )
    except STTServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return result


@router.get("/status")
async def voice_status(current_user: User = Depends(get_current_user)):
    from app.services.voice import is_voice_configured
    from app.services.stt import is_stt_configured

    return {"tts_configured": await is_voice_configured(), "stt_configured": await is_stt_configured()}
