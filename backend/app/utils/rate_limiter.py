import time
import redis
from fastapi import HTTPException, status
from ..config import get_settings

settings = get_settings()
r = redis.from_url(settings.REDIS_URL)

def rate_limit(key: str, limit: int, per_seconds: int = 60):
    now = int(time.time())
    window = now // per_seconds
    rk = f"rl:{key}:{window}"
    count = r.incr(rk)
    if count == 1:
        r.expire(rk, per_seconds)
    if count > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
