import asyncio
from typing import Any


class LocatorService:
    def __init__(self):
        self._container: dict = dict()

    # ----------------------------
    # Singleton eager (ساخت همزمان)
    # ----------------------------
    def registerSingleton(self, key, build_fn):
        """ساخت Singleton در شروع برنامه"""
        instance = build_fn()
        if instance is None:
            raise Exception("not return instance")
        self._container[key] = instance

    async def registerSingletonAsync(self, key, build_fn):
        """ساخت Singleton Async در شروع برنامه"""
        instance = await build_fn()
        if instance is None:
            raise Exception("not return instance")
        self._container[key] = instance

    # ----------------------------
    # Singleton lazy (ساخت هنگام اولین استفاده)
    # ----------------------------
    def registerSingletonLazy(self, key, build_fn):
        """Singleton Lazy (Sync)"""
        instance = None

        def wrapper():
            nonlocal instance
            if instance is None:
                instance = build_fn()
                if instance is None:
                    raise Exception("not return instance")
            return instance

        self._container[key] = wrapper

    def registerSingletonAsyncLazy(self, key, build_fn):
        """Singleton Lazy (Async)"""
        instance = None

        async def wrapper():
            nonlocal instance
            if instance is None:
                instance = await build_fn()
                if instance is None:
                    raise Exception("not return instance")
                return instance

        self._container[key] = wrapper

    # ----------------------------
    # Factory (هر بار نمونه جدید)
    # ----------------------------
    def registerFactory(self, key, build_fn):
        if build_fn() is None:
            raise Exception("not return instance")
        self._container[key] = build_fn

    async def registerFactoryAsync(self, key, build_fn):
        if (await build_fn()) is None:
            raise Exception("not return instance")
        self._container[key] = build_fn

    # ----------------------------
    # دسترسی به سرویس‌ها
    # ----------------------------
    def get(self, key: str) -> Any:
        """دسترسی به سرویس Sync"""
        provider = self._container.get(key, None)
        if provider is None:
            raise ValueError(f"Service {key} not registered")
        if asyncio.iscoroutine(provider):
            raise ValueError(f"Service {key} not sync use get_async")
        if callable(provider):
            return provider()
        return provider

    async def get_async(self, key) -> Any:
        """دسترسی به سرویس Async"""
        provider = self._container.get(key, None)
        if provider is None:
            raise ValueError(f"Service {key} not registered")
        if asyncio.iscoroutine(provider):
            return await provider()  # type: ignore
        if callable(provider):
            return provider()
        return provider


# ------------------ نمونه استفاده ------------------

# if __name__ == "__main__":
#     # سرویس ساده Sync
#     class SyncService:
#         def __init__(self):
#             self.name = "SyncService"

#     # سرویس Async
#     class AsyncService:
#         def __init__(self, value):
#             self.value = value

#     async def build_async_service():
#         await asyncio.sleep(0.1)
#         return AsyncService(42)

#     locator = LocatorService()

#     # Singleton eager
#     locator.registerSingleton("sync_singleton", lambda: SyncService())

#     # Singleton Lazy
#     locator.registerSingletonLazy("sync_singleton_lazy", lambda: SyncService())

#     # Async Singleton eager
#     await locator.registerSingletonAsync("async_singleton", build_async_service)

#     # Async Singleton Lazy
#     locator.registerSingletonAsyncLazy("async_singleton_lazy", build_async_service)

#     # Factory (هر بار نمونه جدید)
#     locator.registerFactory("sync_factory", lambda: SyncService())

#     # Async Factory (هر بار نمونه جدید async)
#     locator.registerFactoryAsync("async_factory", build_async_service)
