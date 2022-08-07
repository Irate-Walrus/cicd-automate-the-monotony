from datetime import datetime
from email.policy import default
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String

from .database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(100))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
