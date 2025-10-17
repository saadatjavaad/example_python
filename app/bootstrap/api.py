from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from backbone.exceptions import (
    BaseHttpException,
    Errhandler,
    Exception422,
)

from backbone.middlewares.auth_middleware import AuthMiddleware
from backbone.middlewares.header_time_middleware import HeaderTimeMiddleware
from bootstrap import setup_app
from routers import all_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_app()
    # redis = Redis.from_url(
    #     configs.REDIS_URI,
    #     encoding=configs.REDIS_ENCODING,
    #     decode_responses=configs.REDIS_RESPONSE_DECODE,
    # )
    # await FastAPILimiter.init(redis)
    yield
    # await redis.close()


app = FastAPI(lifespan=lifespan, dependencies=[])

# EXCEPTIONS
app.add_exception_handler(RequestValidationError, Errhandler.validation_error)
app.add_exception_handler(Exception422, Errhandler.validation_error)
app.add_exception_handler(BaseHttpException, Errhandler.general_error)
app.add_exception_handler(Exception, Errhandler.general_error)

# MIDDLEWARES
app.add_middleware(AuthMiddleware)
app.add_middleware(HeaderTimeMiddleware)
# app.add_middleware(AuthMiddleware)
# app.add_middleware(AddRequestContextMiddleware)
# app.add_middleware(InterceptResponseMiddleWare)
# app.add_middleware(SentryAsgiMiddleware)


for r in all_routers:
    app.include_router(r)
