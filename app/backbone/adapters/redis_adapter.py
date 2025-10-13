import asyncio
import pickle
from typing import Generic, Optional, TypeVar
import coredis
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class RedisAdapterConfig:
    host: str = "localhost"
    port: int = 6379
    snapshot_interval_sec: int = 5
    snapshot_dir: str = r".\data"


class RedisAdapter(Generic[T]):
    def __init__(self, config: RedisAdapterConfig):
        self.config = config
        self.client: Optional[coredis.Redis] = None
        self._snapshot_task: Optional[asyncio.Task] = None
        self._stop_snapshot = False

    async def connect(self):
        self.client = coredis.Redis(host=self.config.host, port=self.config.port)
        await self.client.ping()
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())

    def _make_key(self, key: str, table: Optional[str] = None) -> str:
        """اضافه کردن prefix برای namespace/table"""
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
            await asyncio.sleep(self.config.snapshot_interval_sec)
            if self.client:
                await self.client.bgsave()

    # async def close(self):
    #     self._stop_snapshot = True
    #     if self._snapshot_task:
    #         await self._snapshot_task
    #     if self.client:
    #         self.client.()


if __name__ == "__main__":

    async def main():
        config = RedisAdapterConfig(snapshot_interval_sec=2)
        adapter = RedisAdapter[dict](config)

        await adapter.connect()

        # ذخیره در جدول های جداگانه
        await adapter.set("user1", {"name": "Alice", "age": 30}, table="users")
        await adapter.set("user2", {"name": "Bob", "age": 25}, table="users")
        await adapter.set("user1", {"session": "xyz"}, table="sessions")

        # بازیابی داده ها
        user1 = await adapter.get("user1", table="users")
        session1 = await adapter.get("user1", table="sessions")
        print("user1:", user1)
        print("session1:", session1)

        await asyncio.sleep(10)  # برای snapshot

    asyncio.run(main())
