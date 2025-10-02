from typing import Any, Optional, Union, List, Dict
from redis import asyncio as aioredis
import json
from asyncio import Lock
from contextlib import asynccontextmanager


class RedisPipeline:
    def __init__(self, redis_conn: "RedisConnection"):
        self._redis = redis_conn.pool
        self._pipeline = self._redis.pipeline()

    async def incr(self, key: str) -> "RedisPipeline":
        """Add INCR command to pipeline"""
        await self._pipeline.incr(key)
        return self

    async def expire(self, key: str, seconds: int) -> "RedisPipeline":
        """Add EXPIRE command to pipeline"""
        await self._pipeline.expire(key, seconds)
        return self

    async def execute(self) -> List[Any]:
        """Execute all commands in pipeline"""
        return await self._pipeline.execute()


class RedisConnection:
    _pool: Optional[aioredis.Redis] = None
    _locks: Dict[str, Lock] = {}

    def __init__(self, uri: str = "redis://localhost"):
        self.uri = uri

    async def connect(self) -> None:
        """Connect to Redis"""
        self._pool = await aioredis.from_url(self.uri, decode_responses=True)

    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def rpush(self, key: str, value: Union[str, int]) -> int:
        """Append a value to a list"""
        if not self._pool:
            return 0
        return await self._pool.rpush(key, value)

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Get a range of elements from a list"""
        if not self._pool:
            return []
        return await self._pool.lrange(key, start, end)

    def pipeline(self) -> RedisPipeline:
        """Create a pipeline for executing multiple commands"""
        return RedisPipeline(self)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis and attempt to decode it from JSON"""
        if not self._pool:
            return None

        value = await self._pool.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(
        self, key: str, value: Any, expire: Optional[int] = None, nx: bool = False
    ) -> bool:
        """Set a value in Redis with optional expiration (in seconds)."""
        if not self._pool:
            return False

        try:
            str_value = (
                json.dumps(value) if not isinstance(value, (str, bytes)) else value
            )
            return await self._pool.set(key, str_value, ex=expire, nx=nx)
        except (TypeError, json.JSONEncodeError):
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        if not self._pool:
            return False
        return bool(await self._pool.delete(key))

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        if not self._pool:
            return False
        return bool(await self._pool.exists(key))

    async def increment(self, key: str) -> int:
        """Increment a counter in Redis"""
        if not self._pool:
            return 0
        return await self._pool.incr(key)

    async def decrement(self, key: str) -> int:
        """Decrement a counter in Redis"""
        if not self._pool:
            return 0
        return await self._pool.decr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key"""
        if not self._pool:
            return False
        return bool(await self._pool.expire(key, seconds))

    async def ttl(self, key: str) -> int:
        """Get remaining time to live of a key in seconds"""
        if not self._pool:
            return -2
        return await self._pool.ttl(key)

    async def smembers(self, key: str) -> List[str]:
        """Get all members of a set"""
        if not self._pool:
            return []
        return await self._pool.smembers(key)

    async def sadd(self, key: str, value: str) -> int:
        """Add a member to a set"""
        if not self._pool:
            return 0
        return await self._pool.sadd(key, value)

    @property
    def pool(self) -> aioredis.Redis:
        if not self._pool:
            raise RuntimeError("Redis connection not established")
        return self._pool

    @asynccontextmanager
    async def get_lock(self, key: str):
        """Get a lock for a specific key to prevent race conditions"""
        if key not in self._locks:
            self._locks[key] = Lock()

        async with self._locks[key]:
            yield