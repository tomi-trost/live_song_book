import asyncio
import json
from typing import AsyncGenerator

# All active SSE client queues
_clients: list[asyncio.Queue] = []


def register_client() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _clients.append(q)
    return q


def unregister_client(q: asyncio.Queue) -> None:
    try:
        _clients.remove(q)
    except ValueError:
        pass


async def broadcast(event: str, data: dict) -> None:
    message = f"event: {event}\ndata: {json.dumps(data)}\n\n"
    dead = []
    for q in _clients:
        try:
            q.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        unregister_client(q)


async def event_stream(q: asyncio.Queue) -> AsyncGenerator[str, None]:
    try:
        yield ": connected\n\n"
        while True:
            try:
                message = await asyncio.wait_for(q.get(), timeout=25)
                yield message
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        unregister_client(q)
