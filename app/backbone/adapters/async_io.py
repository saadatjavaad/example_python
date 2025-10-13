# راهنمای استفاده از توابع AsyncAdapter و Multiprocessing

# run_nowait(method, *args, **kwargs)

# زمان استفاده: اجرای یک تابع sync یا async بدون انتظار برای نتیجه، وقتی می‌خواهید کارها همزمان شروع شوند.

# نباید استفاده شود: وقتی نیاز دارید نتیجه تابع بلافاصله در دسترس باشد.

# نکته: مناسب توابع I/O-bound یا blocking کوچک است.

# run_wait(method, *args, **kwargs)

# زمان استفاده: اجرای تابع sync یا async و انتظار برای تکمیل آن.

# نباید استفاده شود: برای توابع بسیار سبک که overhead اجرای thread یا task جدید ایجاد می‌کند.

# نکته: مناسب توابع زمان‌بر یا I/O-heavy است.

# run_after(sec, method, *args, **kwargs)

# زمان استفاده: اجرای تابع بعد از یک تاخیر مشخص.

# نباید استفاده شود: وقتی نیاز به اجرای فوری تابع دارید.

# نکته: می‌توان برای زمان‌بندی کارها یا retry بعد از delay استفاده کرد.

# gather(*methods, return_exceptions=False)

# زمان استفاده: اجرای همزمان چند تابع async یا sync و انتظار برای همه نتایج.

# نباید استفاده شود: وقتی توابع وابسته به هم هستند و باید ترتیب اجرا حفظ شود.

# نکته: مشابه asyncio.gather ولی با پشتیبانی از توابع sync.

# retry_async(method, retries=3, delay=1.0, *args, **kwargs)

# زمان استفاده: اجرای تابع با تلاش مجدد در صورت شکست.

# نباید استفاده شود: وقتی تابع همیشه موفق است یا شکست آن نیاز به مدیریت خاص دارد.

# نکته: مناسب توابع I/O-heavy یا شبکه‌ای است.

# timeout_async(method, timeout, *args, **kwargs)

# زمان استفاده: محدود کردن زمان اجرای یک تابع.

# نباید استفاده شود: وقتی زمان اجرا طولانی قابل قبول است و timeout غیرضروری است.

# نکته: مناسب توابع blocking یا طولانی که ممکن است loop را مسدود کنند.

# map_async(method, iterable, max_concurrency=5)

# زمان استفاده: اجرای همزمان یک تابع روی لیستی از داده‌ها با محدودیت concurrency.

# نباید استفاده شود: وقتی توابع سبک هستند و overhead concurrency زیادتر از سود آن است.

# نکته: کنترل concurrency مهم است تا threadهای زیاد ایجاد نشود.

# run_in_process(method, *args, pool=None, **kwargs)

# زمان استفاده: اجرای یک تابع CPU-bound در یک process جدا برای استفاده از چند هسته.

# نباید استفاده شود: برای توابع I/O-bound کوتاه، چون overhead process زیاد است.

# نکته: می‌توان Pool سفارشی داد یا از pool موقت استفاده کرد.

# map_in_process(method, iterable, pool=None, max_workers=None)

# زمان استفاده: اعمال یک تابع CPU-bound روی یک لیست داده‌ها با multiprocessing.

# نباید استفاده شود: برای توابع سبک یا I/O-bound، overhead زیاد می‌شود.

# نکته: مشابه map_async ولی برای CPU-heavy tasks.

# starmap_in_process(method, iterable, pool=None, max_workers=None)

# زمان استفاده: مشابه map_in_process ولی برای لیست tuple که به عنوان چند آرگومان به تابع می‌رود.

# نباید استفاده شود: وقتی آرگومان‌ها تک‌تایی هستند یا توابع سبک هستند.

# نکته: برای پردازش داده‌های پیچیده یا چند پارامتری مناسب است.


import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable, List, Union


class AsyncIOAdapter:
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def run_nowait(
        self, method: Callable[..., Any], *args, **kwargs
    ) -> Union[asyncio.Task, Awaitable[Any]]:
        try:
            if asyncio.iscoroutinefunction(method):
                return asyncio.create_task(method(*args, **kwargs))
            else:
                return asyncio.get_running_loop().run_in_executor(
                    self.executor, method, *args, **kwargs
                )
        except Exception as e:
            raise Exception(f"Error in run_nowait: {e}")

    async def run_wait(self, method: Callable[..., Any], *args, **kwargs):
        """اجرا به حالت async |"""
        try:
            awaitable = self.run_nowait(method, *args, **kwargs)
            return await awaitable
        except Exception as e:
            raise Exception(f"Error in run_wait: {e}")

    def run_after(
        self, sec: int, method: Callable[..., Any], *args, **kwargs
    ) -> Union[asyncio.Task, Awaitable[Any]]:
        async def f():
            await asyncio.sleep(sec)
            return self.run_nowait(method, *args, **kwargs)

        try:
            return self.run_nowait(f)
        except Exception as e:
            raise Exception(f"Error in run_wait: {e}")

    async def gather(
        self, *methods: Callable[..., Any], return_exceptions: bool = False
    ):
        """
        اجرای همزمان چند متد (async یا sync) و انتظار برای همه
        """
        tasks = [self.run_nowait(m) for m in methods]
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    async def retry_async(
        self,
        method: Callable[..., Any],
        retries: int = 3,
        delay: float = 1.0,
        *args,
        **kwargs,
    ):
        """
        اجرای تابع با تلاش مجدد در صورت خطا
        """
        last_exception = None
        for _ in range(retries):
            try:
                return await self.run_wait(method, *args, **kwargs)
            except Exception as e:
                last_exception = e
                await asyncio.sleep(delay)
        raise last_exception  # type: ignore

    async def timeout_async(
        self, method: Callable[..., Any], timeout: float, *args, **kwargs
    ):
        """
        اجرای تابع async یا sync با محدودیت زمانی
        """
        try:
            return await asyncio.wait_for(
                self.run_wait(method, *args, **kwargs), timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Method {method.__name__} timed out after {timeout} seconds"
            )

    async def map_async(
        self,
        method: Callable[..., Any],
        iterable: List[Any],
        *,
        max_concurrency: int = 5,
    ):
        """
        اجرای همزمان تابع روی آیتم‌های iterable با محدودیت concurrency
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def worker(item):
            async with semaphore:
                return await self.run_wait(method, item)

        tasks = [worker(item) for item in iterable]
        return await asyncio.gather(*tasks)

    async def _then(
        self,
        first_method: Callable[..., Any],
        next_method: Callable[..., Any],
        *args,
        **kwargs,
    ):
        result = await self.run_wait(first_method, *args, **kwargs)
        return await self.run_wait(next_method, result)

    def then(
        self,
        first_method: Callable[..., Any],
        next_method: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Union[asyncio.Task, Awaitable[Any]]:
        """
        اجرای first_method و بعد از آن اجرای next_method با خروجی first_method.
        شبیه به then در فلاتر.
        """
        return self.run_nowait(self._then, first_method, next_method, *args, **kwargs)


# فرض می‌کنیم AsyncIOAdapter از قبل تعریف شده و import شده است
# from async_adapter import AsyncIOAdapter


if __name__ == "__main__":
    adapter = AsyncIOAdapter()

    import asyncio

    # --- توابع sync ---
    def first_sync(x):
        print(f"first_sync  {x}")
        return x + 5

    def second_sync(y):
        print(f"second_sync  {y}")
        return y * 3

    # --- مثال 1: استفاده async ---
    async def main_async():
        print("شروع مثال async")
        result = adapter.then(first_sync, second_sync, 7)

        print(f"نتیجه async: {await result}\n")  # انتظار: (7+10)*2 = 34

    asyncio.run(main_async())
