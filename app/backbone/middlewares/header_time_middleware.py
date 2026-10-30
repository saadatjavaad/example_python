import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class HeaderTimeMiddleware(BaseHTTPMiddleware):
    """
    ثبت درخواست‌ها: method, path, status_code, duration
    اگر مدت زمان زیاد باشد، لاگ هشدار ثبت می‌کند.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start
            logger.error(
                "%s %s - %s (%.4fs)",
                request.method,
                request.url.path,
                exc,
                duration,
            )
            raise

        duration = time.perf_counter() - start
        logger.info(
            "%s %s -> %d (%.4fs)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        response.headers["X-Process-Time"] = f"{duration:.6f}"
        return response
