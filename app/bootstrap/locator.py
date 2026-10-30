from contextlib import asynccontextmanager

import logging

from backbone.adapters.async_auth_adapter import AsyncRedisAuthAdapter
from backbone.adapters.async_redis_adapter import (
    AsyncRedisAdapter,
    AsyncRedisAdapterConfig,
)
from backbone.adapters.file_storage_service import FileStorageService
from backbone.adapters.sms_adapter_kavenegar import SMSAdapter
from backbone.configs import configs as cfg
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.locator_service import LocatorService

logger = logging.getLogger(__name__)

loc = LocatorService()


async def setup():
    logger.info("setup locator ....")

    loc.registerSingleton(  #     cfg: Configs = loc.get("Configs")
        "Configs", lambda: cfg
    )
    await loc.registerSingletonAsync(  #     asyncRedisAdapter: AsyncRedisAdapter = loc.get("AsyncRedisAdapter")
        "AsyncRedisAdapter",
        lambda: AsyncRedisAdapter(
            AsyncRedisAdapterConfig(
                host=loc.get("Configs").REDIS_HOST,
                port=loc.get("Configs").REDIS_PORT,
            )
        ).connect(),
    )
    loc.registerSingleton(  #     asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")
        "AsyncRedisAuthAdapter",
        lambda: AsyncRedisAuthAdapter(
            redis_client=loc.get("AsyncRedisAdapter").client,
            jwt_secret_key=loc.get("Configs").SECRET_KEY,
            otp_expire_seconds=120,
        ),
    )
    logger.info(cfg.POSTGRES_ASYNC_URI)
    loc.registerSingleton(  #     sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
        "SQLAlchemyAdapter",
        lambda: SQLAlchemyAdapter(
            database_url=loc.get("Configs").POSTGRES_ASYNC_URI
        ).initialize(),
    )
    await loc.get("SQLAlchemyAdapter").enums_sync()

    loc.registerSingleton(  #     asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")
        "SMSAdapter",
        lambda: SMSAdapter(
            api_key=loc.get("Configs").KAVENEGAR_ACCESS_KEY,
            sender=loc.get("Configs").KAVENEGAR_SENDER,
        ),
    )
    loc.registerSingleton(  #     fileStorageService: FileStorageService = loc.get("FileStorageService")
        "FileStorageService",
        lambda: FileStorageService(),
    )


async def close():
    loc.get("SQLAlchemyAdapter").dispose()


@asynccontextmanager
async def script():
    """
    متد ویژه اجرای اسکریپت‌ها.
    سینگلتون‌ها را راه‌اندازی کرده و در انتهای کار اتصال دیتابیس را به‌صورت خودکار می‌بندد.
    """
    await setup()
    try:
        yield loc
    finally:
        await close()


# from backbone.db.sqlalchemy_db_based import EnumMixin, SQLAlchemyAdapter
# from bootstrap.locator import script
# import asyncio


# async def main():
#     async with script() as loc:
#         sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
#         with sqlAlchemyAdapter.session_factory() as session:
#             EnumMixin.sync_all_enums(session)


# if __name__ == "__main__":
#     asyncio.run(main())
