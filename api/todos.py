# app/api/todos.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.deps import get_current_user
from app.models import Todo, User as UserModel

class TodoCreate(BaseModel):
    text: str

class TodoOut(BaseModel):
    id: str
    text: str
    done: bool

    class Config:
        orm_mode = True

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


@router.post("", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    todo = Todo(user_id=current_user.id, text=payload.text)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("", response_model=List[TodoOut])
def list_todos(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.user_id == current_user.id).order_by(Todo.created_at.desc()).all()


@router.post("/{todo_id}/complete", response_model=TodoOut)
def complete_todo(todo_id: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    todo.done = True
    db.commit()
    db.refresh(todo)
    return todo