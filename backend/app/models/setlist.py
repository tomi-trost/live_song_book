from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SetlistCreate(BaseModel):
    name: str
    song_ids: list[str] = []


class SetlistUpdate(BaseModel):
    name: Optional[str] = None
    song_ids: Optional[list[str]] = None


class SetlistOut(BaseModel):
    id: str
    name: str
    song_ids: list[str]
    created_at: datetime
