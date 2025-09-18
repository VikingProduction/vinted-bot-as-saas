# backend/app/utils/event_bus.py

import aioredis

REDIS_URL = "redis://localhost:6379"
STREAM_KEY = "vinted_items"

redis = aioredis.from_url(REDIS_URL)

async def publish_event(stream: str, data: dict):
    await redis.xadd(stream, data)
