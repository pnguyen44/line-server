import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Mapping, Optional, cast

import aiofiles
import aioredis
from dotenv import load_dotenv

from line_server.exceptions import IndexOutOfBounds
from line_server.redis.exceptions import RedisConnectionError, RedisError

load_dotenv()

REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_HOST = os.getenv("REDIS_HOST", "host.docker.internal")
BATCH_SIZE = 50


@asynccontextmanager
async def wrap_errors() -> AsyncIterator[None]:
    """Yields and catches any raised by the redis library, re-raising
    with our own exception class."""

    try:
        yield
    except aioredis.RedisError as exc:
        new_exc = RedisError(str(exc))
        raise new_exc from exc


class RedisClient:
    def __init__(self, *, port: int, host: str) -> None:
        self.client = aioredis.from_url(
            f"redis://{host}:{port}", decode_responses=True
        )

    async def ping(self) -> None:
        if not await self.client.ping():
            raise RedisConnectionError("Redis client failure to connect")
        else:
            print("Connected to Redis")

    async def add_to_data_store(self, filename: str) -> None:
        """Adds the content of a file to the data store"""
        count = 0
        data = {}
        async with aiofiles.open(filename) as f:
            async for line in f:
                count += 1
                data[str(count)] = line.strip()

                if count > 0 and count % BATCH_SIZE == 0:
                    await self.bulk_set_key_value(data)
                    data = {}

        if data.keys():
            await self.bulk_set_key_value(data)

    async def bulk_set_key_value(self, data: Mapping[str, Any]) -> None:
        async with self.client.pipeline(transaction=True) as pipe:
            for key, value in data.items():
                async with wrap_errors():
                    await pipe.set(str(key), value)
            async with wrap_errors():
                await pipe.execute()

    async def get_value(self, key: str) -> Optional[str]:
        async with wrap_errors():
            value = await self.client.get(key)

        if value or value == "":
            return cast(str, value)

        raise IndexOutOfBounds

    async def get_keys(self) -> list[str]:
        return cast(list[str], await self.client.keys())

    async def close(self) -> None:
        self.client.close()
        print("Closing connection to Redis")


async def new_redis_client() -> RedisClient:
    client = RedisClient(port=REDIS_PORT, host=REDIS_HOST)
    await client.ping()
    return client
