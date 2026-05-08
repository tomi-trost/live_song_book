from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None


def get_db():
    return client[settings.db_name]


async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.mongo_url)
    db = get_db()
    await db["live_state"].update_one(
        {"_id": "singleton"},
        {"$setOnInsert": {"current_song_id": None, "setlist_id": None, "position": 0, "is_active": False}},
        upsert=True,
    )


async def close_db():
    global client
    if client:
        client.close()
