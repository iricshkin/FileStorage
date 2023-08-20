import json
import uuid
from datetime import datetime
from typing import Any, Callable, Type

from fastapi_cache import caches  # type: ignore
from fastapi_cache.backends.redis import CACHE_KEY  # type: ignore
from fastapi_cache.backends.redis import RedisCacheBackend
from pydantic import BaseModel


def redis_cache():  # type: ignore
    return caches.get(CACHE_KEY)


def serialized_data(value):  # type: ignore
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return str(value)
    return value


async def set_cache(
    cache: RedisCacheBackend, data: dict, redis_key: str, expire: int = 30
) -> Any:
    await cache.set(
        key=redis_key,
        value=json.dumps(data, default=serialized_data),
        expire=expire,
    )


async def get_cache(cache: RedisCacheBackend, redis_key: str) -> Any:
    data = await cache.get(redis_key)
    if data:
        data = json.loads(data)
    return data


async def get_cache_or_data(
    redis_key: str,
    cache: RedisCacheBackend,
    db_func_obj: Callable,
    data_schema: Type[BaseModel],
    db_func_args: tuple = (),
    db_func_kwargs: dict = {},
    cache_expire: int = 30,
) -> Any:
    data = await get_cache(cache, redis_key)
    if not data:
        data = await db_func_obj(*db_func_args, **db_func_kwargs)
        if data:
            data = data_schema.from_orm(data).dict()
            await set_cache(
                cache=cache,
                data=data,
                redis_key=redis_key,
                expire=cache_expire,
            )
        else:
            return None
    return data
