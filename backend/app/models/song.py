from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class SongCreate(BaseModel):
    title: str
    author: str
    content: str  # raw tabdown/chordpro style text


class SongUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    content: Optional[str] = None


class SongOut(BaseModel):
    id: str
    title: str
    author: str
    content: str
    created_at: datetime
    updated_at: datetime
