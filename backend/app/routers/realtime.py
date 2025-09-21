from fastapi import APIRouter, WebSocket
import asyncio
from ..utils.event_bus import redis

router = APIRouter()

@router.websocket("/ws/alerts")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    last_id = "0-0"
    while True:
        resp = await redis.xread({"vinted_items": last_id}, count=10, block=0)
        if resp:
            stream, messages = resp[0]
            for msg_id, data in messages:
                last_id = msg_id
                await ws.send_json(data)
        else:
            await asyncio.sleep(0.1)
