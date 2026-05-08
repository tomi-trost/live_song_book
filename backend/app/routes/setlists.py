from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone
from app.database import get_db
from app.models.setlist import SetlistCreate, SetlistUpdate, SetlistOut
from app.services.auth import get_current_admin

router = APIRouter(prefix="/api/setlists", tags=["setlists"])


def _serialize(doc) -> SetlistOut:
    return SetlistOut(
        id=str(doc["_id"]),
        name=doc["name"],
        song_ids=doc.get("song_ids", []),
        created_at=doc["created_at"],
    )


@router.get("", response_model=list[SetlistOut])
async def list_setlists(_: str = Depends(get_current_admin)):
    db = get_db()
    docs = await db["setlists"].find().sort("created_at", -1).to_list(length=100)
    return [_serialize(d) for d in docs]


@router.get("/{setlist_id}", response_model=SetlistOut)
async def get_setlist(setlist_id: str, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(setlist_id):
        raise HTTPException(status_code=404, detail="Setlist not found")
    doc = await db["setlists"].find_one({"_id": ObjectId(setlist_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Setlist not found")
    return _serialize(doc)


@router.post("", response_model=SetlistOut, status_code=201)
async def create_setlist(body: SetlistCreate, _: str = Depends(get_current_admin)):
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {**body.model_dump(), "created_at": now}
    result = await db["setlists"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.patch("/{setlist_id}", response_model=SetlistOut)
async def update_setlist(setlist_id: str, body: SetlistUpdate, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(setlist_id):
        raise HTTPException(status_code=404, detail="Setlist not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db["setlists"].find_one_and_update(
        {"_id": ObjectId(setlist_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Setlist not found")
    return _serialize(result)


@router.delete("/{setlist_id}", status_code=204)
async def delete_setlist(setlist_id: str, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(setlist_id):
        raise HTTPException(status_code=404, detail="Setlist not found")
    result = await db["setlists"].delete_one({"_id": ObjectId(setlist_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Setlist not found")
