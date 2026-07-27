from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Reminder, utcnow

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


class ReminderCreate(BaseModel):
    text: str
    remind_at: datetime


class ReminderOut(BaseModel):
    id: str
    text: str
    remind_at: datetime
    done: bool
    notified: bool

    model_config = {"from_attributes": True}


@router.post("", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    reminder = Reminder(user_id=current_user.id, text=payload.text, remind_at=payload.remind_at)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("", response_model=List[ReminderOut])
def list_reminders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Reminder)
        .filter(Reminder.user_id == current_user.id, Reminder.done == False)  # noqa: E712
        .order_by(Reminder.remind_at)
        .all()
    )


@router.get("/due", response_model=List[ReminderOut])
def list_due_reminders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lembretes cujo horário já chegou e que ainda não foram concluídos.
    É o papel que uma fila Redis/Celery cumpriria empurrando notificações —
    aqui o Neural Core faz o mesmo efeito com polling (chamar esse endpoint
    a cada N segundos). Marca como 'notified' na hora que é lido, pra não
    reexibir o mesmo aviso repetidamente.
    """
    due = (
        db.query(Reminder)
        .filter(
            Reminder.user_id == current_user.id,
            Reminder.done == False,  # noqa: E712
            Reminder.notified == False,  # noqa: E712
            Reminder.remind_at <= utcnow(),
        )
        .order_by(Reminder.remind_at)
        .all()
    )
    for reminder in due:
        reminder.notified = True
    if due:
        db.commit()
    return due


@router.post("/{reminder_id}/complete", response_model=ReminderOut)
def complete_reminder(
    reminder_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lembrete não encontrado")
    reminder.done = True
    db.commit()
    db.refresh(reminder)
    return reminder
