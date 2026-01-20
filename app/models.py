from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Note(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    content: str
    created_at: datetime
