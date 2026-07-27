"""
Email sender helper supporting SMTP.
Configure SMTP_* variables in settings (.env):
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SMTP_USE_TLS (bool)
If aiosmtplib is available, uses it for async send; otherwise uses smtplib sync fallback.
"""
import logging
from typing import Optional
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("tools.email")

SMTP_HOST = getattr(settings, "SMTP_HOST", "")
SMTP_PORT = int(getattr(settings, "SMTP_PORT", 587))
SMTP_USER = getattr(settings, "SMTP_USER", "")
SMTP_PASSWORD = getattr(settings, "SMTP_PASSWORD", "")
SMTP_USE_TLS = bool(getattr(settings, "SMTP_USE_TLS", True))

try:
    import aiosmtplib  # type: ignore
    _HAS_AIOSMTP = True
except Exception:
    _HAS_AIOSMTP = False
    import smtplib

async def send_email(to: str, subject: str, body: str, html: Optional[str] = None, sender: Optional[str] = None) -> dict:
    sender = sender or getattr(settings, "SMTP_DEFAULT_FROM", SMTP_USER or "noreply@example.com")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    if _HAS_AIOSMTP:
        try:
            await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, username=SMTP_USER or None, password=SMTP_PASSWORD or None, start_tls=SMTP_USE_TLS)
            return {"ok": True}
        except Exception as exc:
            logger.exception("aiosmtplib send failed: %s", exc)
            return {"ok": False, "error": str(exc)}
    else:
        try:
            if SMTP_USE_TLS:
                s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
                s.starttls()
            else:
                s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            if SMTP_USER and SMTP_PASSWORD:
                s.login(SMTP_USER, SMTP_PASSWORD)
            s.send_message(msg)
            s.quit()
            return {"ok": True}
        except Exception as exc:
            logger.exception("smtplib send failed: %s", exc)
            return {"ok": False, "error": str(exc)}