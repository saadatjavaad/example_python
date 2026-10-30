import asyncio
import logging
import pickle
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar
import redis.asyncio as redis

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class AsyncRedisAdapterConfig:
    host: str = "localhost"
    port: int = 6379
    snapshot_interval_sec: int = 5
    snapshot_dir: str = r".\data"


class AsyncRedisAdapter(Generic[T]):
    def __init__(self, config: AsyncRedisAdapterConfig):
        self.config = config
        self.client: Optional[redis.Redis] = None
        self._snapshot_task: Optional[asyncio.Task] = None
        self._stop_snapshot = False

    async def connect(self):
        self.client = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            decode_responses=False,  # برای کار با داده‌های باینری (pickle)
        )
        await self.client.ping()
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())
        return self

    def _make_key(self, key: str, table: Optional[str] = None) -> str:
        if table:
            return f"{table}:{key}"
        return key

    async def set(self, key: str, value: T, table: Optional[str] = None):
        if self.client:
            serialized = pickle.dumps(value)
            namespaced_key = self._make_key(key, table)
            await self.client.set(namespaced_key, serialized)

    async def get(self, key: str, table: Optional[str] = None) -> Optional[T]:
        if self.client:
            namespaced_key = self._make_key(key, table)
            raw = await self.client.get(namespaced_key)
            if raw is not None:
                return pickle.loads(raw)
        return None

    async def _snapshot_loop(self):
        while not self._stop_snapshot:
            try:
                await asyncio.sleep(self.config.snapshot_interval_sec)
                if self.client and not self._stop_snapshot:
                    await self.client.bgsave()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("Snapshot error: %s", e)

    async def close(self):
        self._stop_snapshot = True
        if self._snapshot_task:
            self._snapshot_task.cancel()
            try:
                await self._snapshot_task
            except asyncio.CancelledError:
                pass
        if self.client:
            await self.client.aclose()


if __name__ == "__main__":

    async def main():
        config = AsyncRedisAdapterConfig(snapshot_interval_sec=2)
        adapter = AsyncRedisAdapter[dict](config)

        await adapter.connect()

        try:
            # ذخیره داده‌ها
            await adapter.set("user1", {"name": "Alice", "age": 30}, table="users")
            await adapter.set("user2", {"name": "Bob", "age": 25}, table="users")
            await adapter.set("user1", {"session": "xyz"}, table="sessions")

            # بازیابی داده‌ها
            user1 = await adapter.get("user1", table="users")
            session1 = await adapter.get("user1", table="sessions")
            print("user1:", user1)
            print("session1:", session1)

            await asyncio.sleep(5)
        finally:
            await adapter.close()

    asyncio.run(main())
