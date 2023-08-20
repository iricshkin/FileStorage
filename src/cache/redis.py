from redis import asyncio as aioredis  # type: ignore

from core.config import app_settings

connection = aioredis.Redis(  # type: ignore
    host=app_settings.redis_host,
    port=app_settings.redis_port,
    decode_responses=True,
)
