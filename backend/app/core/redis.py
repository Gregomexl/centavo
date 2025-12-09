"""Redis client configuration."""
from redis.asyncio import Redis, from_url

from app.config import get_settings

settings = get_settings()


async def get_redis_client() -> Redis:
    """Get Redis client instance."""
    return from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
    )
