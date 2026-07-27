# app/api/voice.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.database import get_db
from app.services.voice import is_voice_configured, synthesize_speech, VoiceNotConfiguredError, VoiceServiceError
from app.services.stt import is_stt_configured, transcribe_audio, STTNotConfiguredError, STTServiceError

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


@router.get("/status")
async def voice_status(user=Depends(get_current_user)):
    tts = await is_voice_configured()
    stt = await is_stt_configured()
    return {"tts_configured": tts, "stt_configured": stt}


@router.post("/speak")
async def speak(payload: dict, user=Depends(get_current_user)):
    text = payload.get("text", "")
    voice_id = payload.get("voice_id")
    try:
        audio = await synthesize_speech(text, voice_id=voice_id)
    except VoiceNotConfiguredError:
        raise HTTPException(status_code=503, detail="ELEVENLABS_API_KEY not configured")
    except VoiceServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return (audio)
    # Note: In FastAPI you'd normally return StreamingResponse or Response with media_type="audio/mpeg".
    # If integrating directly, return Response(content=audio, media_type="audio/mpeg") in your implementation.


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), user=Depends(get_current_user)):
    content = await file.read()
    try:
        result = await transcribe_audio(content, content_type=file.content_type)
    except STTNotConfiguredError:
        raise HTTPException(status_code=503, detail="DEEPGRAM_API_KEY not configured")
    except STTServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return result