from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from bson import ObjectId
from app.database import get_db
from app.models.live import LiveState, SetSongRequest, StartSetlistRequest
from app.services.auth import get_current_admin
from app.services import sse

router = APIRouter(prefix="/api/live", tags=["live"])


async def _get_state(db) -> dict:
    return await db["live_state"].find_one({"_id": "singleton"})


async def _broadcast_state(db):
    state = await _get_state(db)
    song = None
    if state.get("current_song_id"):
        song_doc = await db["songs"].find_one({"_id": ObjectId(state["current_song_id"])})
        if song_doc:
            song = {
                "id": str(song_doc["_id"]),
                "title": song_doc["title"],
                "author": song_doc["author"],
                "content": song_doc["content"],
            }
    await sse.broadcast("state", {
        "is_active": state.get("is_active", False),
        "current_song_id": state.get("current_song_id"),
        "setlist_id": state.get("setlist_id"),
        "position": state.get("position", 0),
        "song": song,
    })


@router.get("/stream")
async def stream():
    q = sse.register_client()
    return StreamingResponse(
        sse.event_stream(q),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/state")
async def get_state():
    db = get_db()
    state = await _get_state(db)
    song = None
    if state.get("current_song_id"):
        song_doc = await db["songs"].find_one({"_id": ObjectId(state["current_song_id"])})
        if song_doc:
            song = {
                "id": str(song_doc["_id"]),
                "title": song_doc["title"],
                "author": song_doc["author"],
                "content": song_doc["content"],
            }
    return {
        "is_active": state.get("is_active", False),
        "current_song_id": state.get("current_song_id"),
        "setlist_id": state.get("setlist_id"),
        "position": state.get("position", 0),
        "song": song,
    }


@router.post("/start")
async def start_setlist(body: StartSetlistRequest, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(body.setlist_id):
        raise HTTPException(status_code=404, detail="Setlist not found")
    setlist = await db["setlists"].find_one({"_id": ObjectId(body.setlist_id)})
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    first_song_id = setlist["song_ids"][0] if setlist["song_ids"] else None
    await db["live_state"].update_one(
        {"_id": "singleton"},
        {"$set": {
            "is_active": True,
            "setlist_id": body.setlist_id,
            "position": 0,
            "current_song_id": first_song_id,
        }},
    )
    await _broadcast_state(db)
    return {"ok": True}


@router.post("/stop")
async def stop(_: str = Depends(get_current_admin)):
    db = get_db()
    await db["live_state"].update_one(
        {"_id": "singleton"},
        {"$set": {"is_active": False, "current_song_id": None, "setlist_id": None, "position": 0}},
    )
    await _broadcast_state(db)
    return {"ok": True}


@router.post("/song")
async def set_song(body: SetSongRequest, _: str = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(body.song_id):
        raise HTTPException(status_code=404, detail="Song not found")
    song = await db["songs"].find_one({"_id": ObjectId(body.song_id)})
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    state = await _get_state(db)
    position = state.get("position", 0)
    if state.get("setlist_id"):
        setlist = await db["setlists"].find_one({"_id": ObjectId(state["setlist_id"])})
        if setlist and body.song_id in setlist["song_ids"]:
            position = setlist["song_ids"].index(body.song_id)
    await db["live_state"].update_one(
        {"_id": "singleton"},
        {"$set": {"current_song_id": body.song_id, "is_active": True, "position": position}},
    )
    await _broadcast_state(db)
    return {"ok": True}


@router.post("/next")
async def next_song(_: str = Depends(get_current_admin)):
    db = get_db()
    state = await _get_state(db)
    if not state.get("setlist_id"):
        raise HTTPException(status_code=400, detail="No active setlist")
    setlist = await db["setlists"].find_one({"_id": ObjectId(state["setlist_id"])})
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    pos = state.get("position", 0) + 1
    if pos >= len(setlist["song_ids"]):
        raise HTTPException(status_code=400, detail="Already at last song")
    next_id = setlist["song_ids"][pos]
    await db["live_state"].update_one(
        {"_id": "singleton"},
        {"$set": {"position": pos, "current_song_id": next_id}},
    )
    await _broadcast_state(db)
    return {"ok": True}


@router.post("/prev")
async def prev_song(_: str = Depends(get_current_admin)):
    db = get_db()
    state = await _get_state(db)
    if not state.get("setlist_id"):
        raise HTTPException(status_code=400, detail="No active setlist")
    setlist = await db["setlists"].find_one({"_id": ObjectId(state["setlist_id"])})
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    pos = state.get("position", 0) - 1
    if pos < 0:
        raise HTTPException(status_code=400, detail="Already at first song")
    prev_id = setlist["song_ids"][pos]
    await db["live_state"].update_one(
        {"_id": "singleton"},
        {"$set": {"position": pos, "current_song_id": prev_id}},
    )
    await _broadcast_state(db)
    return {"ok": True}
