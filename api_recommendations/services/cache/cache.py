import uuid
from abc import ABC, abstractmethod
from enum import Enum

import orjson
import pydantic as pd
from core import config
from redis.asyncio import Redis
from redis.exceptions import RedisError
from services.cache.logger_config import logger


def custom_dumps(obj: pd.BaseModel | dict | list) -> dict:
    if isinstance(obj, pd.BaseModel):
        obj = obj.model_dump()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, uuid.UUID):
                obj[key] = str(value)
            elif isinstance(value, Enum):
                obj[key] = str(value)
            elif isinstance(value, list):
                for x in value:
                    x = custom_dumps(x)
    return obj


class Cache(ABC):

    @abstractmethod
    def set(self, cache_key, data):
        pass

    @abstractmethod
    def get(self, cache_key):
        pass


class RedisCache(Cache):

    def __init__(self, redis: Redis):
        self.redis: Redis = redis

    async def set(self, cache_key: str, data: dict | list):
        data = custom_dumps(data)
        data = orjson.dumps(data)
        try:
            await self.redis.set(cache_key, data, config.REDIS_CACHE_EXPIRES_IN_SECONDS)
            logger.debug('set by {}, {}'.format(cache_key, str(data)[:10]))
        except (TypeError, RedisError) as e:
            logger.error("can't set by {}, {}".format(cache_key, e))

    async def get(self, cache_key: str) -> dict | list | None:
        try:
            data: bytes = await self.redis.get(cache_key)
            if data is not None:
                data: dict | list = orjson.loads(data)
                logger.debug('get by {}, {} '.format(cache_key, str(data)[:10]))
            return data
        except RedisError as e:
            logger.error("can't get by {}, {}".format(cache_key, e))
            return None
