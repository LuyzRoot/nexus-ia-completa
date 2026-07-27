"""
Audio utilities:
- transcribe_audio(bytes, content_type) -> text (tries whisper/whisperx or OpenAI)
- synthesize_speech(text, voice_id) -> bytes (tries ElevenLabs then pyttsx3 fallback)
"""
import logging
from typing import Optional
import io

logger = logging.getLogger("multimodal.audio")

# Try whisper (open-source)
try:
    import whisper  # type: ignore
    _HAS_WHISPER = True
except Exception:
    whisper = None
    _HAS_WHISPER = False

# Try openai audio api fallback
try:
    import openai  # type: ignore
    _HAS_OPENAI = True
except Exception:
    openai = None
    _HAS_OPENAI = False

# TTS: elevenlabs
try:
    from elevenlabs import generate as eleven_generate, set_api_key as eleven_set_key  # type: ignore
    _HAS_ELEVEN = True
except Exception:
    eleven_generate = None
    eleven_set_key = None
    _HAS_ELEVEN = False

# pyttsx3 fallback (sync)
try:
    import pyttsx3  # type: ignore
    _HAS_PYTTSX3 = True
except Exception:
    pyttsx3 = None
    _HAS_PYTTSX3 = False


async def transcribe_audio(content: bytes, content_type: Optional[str] = None) -> str:
    """
    Transcribe audio bytes.
    """
    if _HAS_WHISPER:
        try:
            model = whisper.load_model("small")
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                tmp.write(content)
                tmp.flush()
                result = model.transcribe(tmp.name)
                return result.get("text", "").strip()
        except Exception as exc:
            logger.warning("Whisper transcription failed: %s", exc)
    if _HAS_OPENAI:
        try:
            # openai.Audio.transcriptions endpoint expects a file object; adjust if needed
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                tmp.write(content)
                tmp.flush()
                resp = openai.Audio.transcribe("whisper-1", open(tmp.name, "rb"))
                return resp.get("text", "").strip()
        except Exception as exc:
            logger.warning("OpenAI transcription failed: %s", exc)
    raise RuntimeError("No ASR backend available (install whisper or configure OpenAI)")


async def synthesize_speech(text: str, voice: Optional[str] = None) -> bytes:
    """
    Return audio bytes (wav or mp3). Prefer ElevenLabs; fallback to pyttsx3 generating a temp file and returning bytes.
    """
    if _HAS_ELEVEN:
        try:
            # ensure API key configured via environment or settings
            audio = eleven_generate(text=text, voice=voice or "alloy", model="eleven_multilingual_v1")
            # eleven_generate returns binary audio content depending on library version
            if isinstance(audio, bytes):
                return audio
            # if returns a stream-like object
            buf = io.BytesIO()
            buf.write(audio)
            return buf.getvalue()
        except Exception as exc:
            logger.warning("ElevenLabs TTS failed: %s", exc)
    if _HAS_PYTTSX3:
        try:
            engine = pyttsx3.init()
            import tempfile
            fname = None
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                fname = tmp.name
            engine.save_to_file(text, fname)
            engine.runAndWait()
            with open(fname, "rb") as fh:
                data = fh.read()
            return data
        except Exception as exc:
            logger.warning("pyttsx3 TTS failed: %s", exc)
    raise RuntimeError("No TTS backend available (install elevenlabs or pyttsx3)")