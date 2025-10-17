from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backbone.adapters.auth_adapter import AuthAdapter, LoginEx
from backbone.exceptions import (
    Exception401ExpiredToken,
    Exception401MissingToken,
)
from bootstrap.setup_locator import loc


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        route = request.scope.get("route")
        if route:
            route_tags = getattr(route, "tags", [])
            if "public" in route_tags:
                return await call_next(request)

        authAdapter: AuthAdapter = loc.get("AuthAdapter")
        bToken = request.headers.get("authorization")
        if not bToken:
            raise Exception401MissingToken()
        if not bToken.startswith("Bearer "):
            raise Exception401MissingToken()
        token = bToken.split(" ", 1)[1]
        userOrEx = await authAdapter.get_user_by_token(token)
        if isinstance(userOrEx, LoginEx):
            raise Exception401ExpiredToken()

        request.state.token = token
        request.state.bToken = bToken
        request.state.user = userOrEx

        response: Response = await call_next(request)

        return response
