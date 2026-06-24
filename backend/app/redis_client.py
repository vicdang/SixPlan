import logging
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    global _client
    try:
        if _client is None:
            _client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await _client.ping()
        return _client
    except Exception as e:
        logger.warning("Redis unavailable: %s", e)
        _client = None
        return None
