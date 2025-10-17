import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class HeaderTimeMiddleware(BaseHTTPMiddleware):
    """
    لاگ کردن روشنی از درخواست:
    - method, path, status_code, duration
    - اگر مدت زمان زیاد باشد، لاگ هشدار می‌دهد
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # می‌توان لاگ خطا انجام داد یا پاسخ استاندارد برگرداند
            duration = time.perf_counter() - start
            # اینجا فقط دوباره خطا را پرتاب می‌کنیم بعد از لاگ
            print(
                f"[ERROR] {request.method} {request.url.path} - {exc} ({duration:.4f}s)"
            )
            raise

        duration = time.perf_counter() - start
        print(
            f"[LOG] {request.method} {request.url.path} -> {response.status_code} ({duration:.4f}s)"
        )
        # اضافه کردن هدر اختیاری
        response.headers["X-Process-Time"] = f"{duration:.6f}"
        return response
