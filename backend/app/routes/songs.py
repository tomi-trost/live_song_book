import json
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
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


@router.post("/import", status_code=201)
async def import_songs(file: UploadFile = File(...), _: str = Depends(get_current_admin)):
    raw = await file.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")

    if not isinstance(data, list):
        raise HTTPException(status_code=422, detail="JSON must be an array of song objects")
    if len(data) == 0:
        raise HTTPException(status_code=422, detail="JSON array is empty")

    errors = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append({"index": i, "error": "Each item must be a JSON object"})
            continue
        for field in ("title", "author", "content"):
            if field not in item:
                errors.append({"index": i, "error": f"Missing required field: '{field}'"})
            elif not isinstance(item[field], str):
                errors.append({"index": i, "error": f"Field '{field}' must be a string"})
            elif not item[field].strip():
                errors.append({"index": i, "error": f"Field '{field}' must not be empty"})

    if errors:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "errors": errors})

    now = datetime.now(timezone.utc)
    docs = [
        {
            "title": item["title"].strip(),
            "author": item["author"].strip(),
            "content": item["content"],
            "created_at": now,
            "updated_at": now,
        }
        for item in data
    ]
    db = get_db()
    result = await db["songs"].insert_many(docs)
    return {"imported": len(result.inserted_ids)}


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
