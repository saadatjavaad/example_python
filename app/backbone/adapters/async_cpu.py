import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Any, List, Optional
import cloudpickle  # type: ignore

# اگه کارها خیلی سبک هستن → gather ساده مشکلی نداره.

# اگه کارها سنگین هستن → یا Semaphore بذار (مثلاً ۱۰۰ یا ۵۰۰ تا همزمان)، یا batch‌ای اجرا کن.

# اگر به stream نتیجه‌ها نیاز داری → از as_completed یا yield استفاده کن.


def _cloudpickle_runner(pickled_func: bytes, args: tuple, kwargs: dict) -> Any:
    func = cloudpickle.loads(pickled_func)
    return func(*args, **kwargs)


class AsyncCPUAdapter:
    def __init__(self, max_workers: Optional[int] = None):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    async def run(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        اجرای یک تابع CPU-bound به صورت async
        """
        loop = asyncio.get_running_loop()
        pickled_func = cloudpickle.dumps(func)
        result = await loop.run_in_executor(
            self.executor, _cloudpickle_runner, pickled_func, args, kwargs
        )
        return result

    async def run_multiple(
        self, func: Callable[..., Any], args_list: List[tuple]
    ) -> List[Any]:
        """
        اجرای چند task به صورت همزمان و گرفتن نتایج
        """
        tasks = [self.run(func, *args) for args in args_list]
        return await asyncio.gather(*tasks)

    def shutdown(self, wait: bool = True):
        self.executor.shutdown(wait=wait)

    async def run_multiple_limited(
        self, func: Callable[..., Any], args_list: List[tuple], limit: int = 100
    ) -> List[Any]:
        """
        اجرای چند task به صورت محدود (کنترل همزمانی)
        """
        sem = asyncio.Semaphore(limit)

        async def sem_task(args):
            async with sem:
                return await self.run(func, *args)

        tasks = [sem_task(args) for args in args_list]
        return await asyncio.gather(*tasks)

    async def run_multiple_stream(
        self, func: Callable[..., Any], args_list: List[tuple], limit: int = 100
    ):
        """
        async for res in adapter.run_multiple_stream(func, args_list, limit=50):
            print("got:", res)

        """
        sem = asyncio.Semaphore(limit)

        async def sem_task(args):
            async with sem:
                return await self.run(func, *args)

        coros = [sem_task(args) for args in args_list]
        for fut in asyncio.as_completed(coros):
            result = await fut
            yield result  # یکی یکی آماده‌ها رو بده

    async def run_in_batches(
        self, func: Callable[..., Any], args_list: List[tuple], batch_size: int = 500
    ):
        """
        تکه تکه  (دسته‌دسته) اجرا کنیم
        """
        results = []
        for i in range(0, len(args_list), batch_size):
            batch = args_list[i : i + batch_size]
            results.extend(await self.run_multiple(func, batch))
        return results


# ---- تست ----
def cpu_task(x):
    _ = sum(i * i for i in range(10_000_000))
    return f"process {x} done"


async def main():
    adapter = AsyncCPUAdapter(max_workers=4)

    # اجرای تک task
    result = await adapter.run(cpu_task, 1)
    print(result)

    # اجرای چند task همزمان
    results = await adapter.run_multiple(cpu_task, [(2,), (3,), (4,)])
    print(results)

    # اجرای لامبدا (که به صورت پیشفرض picklable نیست!)
    lam = lambda y: y**2  # noqa: E731
    lam_result = await adapter.run(lam, 5)
    print("lambda:", lam_result)

    adapter.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
