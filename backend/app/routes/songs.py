from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone
from app.database import get_db
from app.models.song import SongCreate, SongUpdate, SongOut
from app.services.auth import get_current_admin

router = APIRouter(prefix="/api/songs", tags=["songs"])


def _serialize(doc) -> SongOut:
    return SongOut(
        id=str(doc["_id"]),
        title=doc["title"],
        author=doc["author"],
        content=doc["content"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("", response_model=list[SongOut])
async def list_songs():
    db = get_db()
    songs = await db["songs"].find().sort("title", 1).to_list(length=1000)
    return [_serialize(s) for s in songs]


@router.get("/{song_id}", response_model=SongOut)
async def get_song(song_id: str):
    db = get_db()
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=404, detail="Song not found")
    doc = await db["songs"].find_one({"_id": ObjectId(song_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Song not found")
    return _serialize(doc)


@router.post("", response_model=SongOut, status_code=201)
async def create_song(body: SongCreate, _: str = Depends(get_current_admin)):
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {**body.model_dump(), "created_at": now, "updated_at": now}
    result = await db["songs"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.patch("/{song_id}", response_model=SongOut)
async def update_song(song_id: str, body: SongUpdate, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=404, detail="Song not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc)
    result = await db["songs"].find_one_and_update(
        {"_id": ObjectId(song_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Song not found")
    return _serialize(result)


@router.delete("/{song_id}", status_code=204)
async def delete_song(song_id: str, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=404, detail="Song not found")
    result = await db["songs"].delete_one({"_id": ObjectId(song_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Song not found")
