import logging

from backbone.adapters.async_auth_adapter import AsyncRedisAuthAdapter
from backbone.exceptions import (
    Exception401ExpiredToken,
    Exception401MissingToken,
)
from bootstrap.locator import loc
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

PUBLIC_PATH_PREFIXES = [
    "/auth/",
    "/docs",
    "/files",
]


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise Exception401MissingToken()

        token = auth_header[7:].strip()
        if not token:
            raise Exception401MissingToken()

        user = await asyncRedisAuthAdapter.get_info_by_token(token)
        if user is None:
            raise Exception401ExpiredToken()

        request.state.token = user
        request.state.user = user

        response: Response = await call_next(request)

        return response
