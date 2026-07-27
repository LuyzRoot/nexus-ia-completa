# app/api/reminders.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Reminder, User as UserModel
from app.schemas import MemoryOut  # reuse schema? we have ReminderOut in original; define inline for brevity
from pydantic import BaseModel
from datetime import datetime

class ReminderCreate(BaseModel):
    text: str
    remind_at: datetime

class ReminderOut(BaseModel):
    id: str
    text: str
    remind_at: datetime
    done: bool
    notified: bool

    class Config:
        orm_mode = True

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


@router.post("", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    reminder = Reminder(user_id=current_user.id, text=payload.text, remind_at=payload.remind_at)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("", response_model=List[ReminderOut])
def list_reminders(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return db.query(Reminder).filter(Reminder.user_id == current_user.id, Reminder.done == False).order_by(Reminder.remind_at).all()


@router.get("/due", response_model=List[ReminderOut])
def list_due_reminders(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    from app.models import utcnow
    due = db.query(Reminder).filter(Reminder.user_id == current_user.id, Reminder.done == False, Reminder.notified == False, Reminder.remind_at <= utcnow()).order_by(Reminder.remind_at).all()
    for r in due:
        r.notified = True
    if due:
        db.commit()
    return due


@router.post("/{reminder_id}/complete", response_model=ReminderOut)
def complete_reminder(reminder_id: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lembrete não encontrado")
    reminder.done = True
    db.commit()
    db.refresh(reminder)
    return reminder