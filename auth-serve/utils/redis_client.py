
import json
import redis.asyncio as redis
from typing import Dict

from config.settings import settings

MIN = 60  # seconds
HOUR = MIN * 60
DAY = HOUR * 24

class RedisClient(redis.Redis):
    def __init__(self, expire: int = None):
        super().__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
        if not expire:
            self.ex = settings.REDIS_KEY_EXPIRATION_TIME
        else:
            self.ex = expire
        
    
    async def set_dict(self, key: str, value: Dict, expire: int = None):
        """
        Set a key-value pair in Redis. The value is a JSON-formatted
        dictionary. If expire is None, the default expiration time
        is used. Otherwise, the given expiration time is used.
        """
        value = json.dumps(value, default=str)
        if expire:
            await self.set(key, value, ex=expire)
        else:
            await self.set(key, value, ex=self.ex)
        
    async def get_dict(self, key: str):
        """
        Get a key-value pair from Redis. The value is a JSON-formatted
        dictionary. If the key does not exist, return None.
        """
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None