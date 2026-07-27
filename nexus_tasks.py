from enum import Enum
from datetime import datetime
from typing import Optional, List
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    def __init__(self, title: str, description: str = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[str] = None
        self.error: Optional[str] = None
        self.subtasks: List["Task"] = []
    
    def start(self):
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self, result: str):
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result
    
    def fail(self, error: str):
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error