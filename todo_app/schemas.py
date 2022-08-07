from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    completed: bool = False

    class Config:
        orm_mode = True


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str]
    completed: Optional[bool]


class Todo(TodoBase):
    id: UUID
    created_at: datetime
