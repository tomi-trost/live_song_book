from pydantic import BaseModel
from typing import Optional


class LiveState(BaseModel):
    is_active: bool
    current_song_id: Optional[str] = None
    setlist_id: Optional[str] = None
    position: int = 0


class SetSongRequest(BaseModel):
    song_id: str


class StartSetlistRequest(BaseModel):
    setlist_id: str
