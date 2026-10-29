from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles

from backbone.exceptions import (
    BaseHttpException,
    Errhandler,
    Exception422,
)
from backbone.middlewares.auth_middleware import AuthMiddleware
from backbone.middlewares.header_time_middleware import HeaderTimeMiddleware
from backbone.middlewares.logger_middelware import RequestResponseLoggerMiddleware
from bootstrap.locator import close, setup
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from routers.auth import router as auth_router
from routers.feedback import router as feedback_router
from routers.gift import router as gift_router
from routers.notification import router as notification_router
from routers.progress_log import router as progress_log_router
from routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup()
    # await FastAPILimiter.init(redis)

    yield
    await close()


app = FastAPI(lifespan=lifespan, dependencies=[])

# EXCEPTIONS
app.add_exception_handler(RequestValidationError, Errhandler.validation_error)
app.add_exception_handler(Exception422, Errhandler.validation_error)
app.add_exception_handler(BaseHttpException, Errhandler.general_error)
app.add_exception_handler(Exception, Errhandler.general_error)

# MIDDLEWARES
app.add_middleware(AuthMiddleware)
app.add_middleware(HeaderTimeMiddleware)
app.add_middleware(RequestResponseLoggerMiddleware)
# app.add_middleware(AuthMiddleware)
# app.add_middleware(AddRequestContextMiddleware)
# app.add_middleware(InterceptResponseMiddleWare)
# app.add_middleware(SentryAsgiMiddleware)

app.mount(
    "/files",
    StaticFiles(directory="storage"),
    name="files",
)

all_routers = [
    auth_router,
    user_router,
    progress_log_router,
    gift_router,
    feedback_router,
    notification_router,
]
for r in all_routers:
    app.include_router(r)
