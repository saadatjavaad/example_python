from pathlib import Path
from urllib.parse import quote
from pydantic_settings import BaseSettings, SettingsConfigDict
import re
from typing import List, Pattern
import sysconfig

BASE_DIR = Path(__file__).resolve().parent.parent.parent
site_packages_path = sysconfig.get_path("purelib")


class Configs(BaseSettings):
    DEBUG: bool = True

    SECRET_KEY: str = "changeme"
    BASE_DIR: Path = BASE_DIR
    PYTHONPATH: str = f"{site_packages_path};{BASE_DIR}/app"

    # PYTHONPATH: list[str] = [
    #     f"{site_packages_path}",
    #     f"${BASE_DIR}/app",
    # ]  # مسیر هایی  که پروژه و شکل وارد کردن را نمایش میدهد

    # API
    # from typing import List, Pattern

    ALLOWED_DOMAIN: List[Pattern[str] | str] = [
        re.compile(r"^https:\/\/(?:.*\.)?timez\.ir$"),
        re.compile(r"^http:\/\/localhost:\d+$"),
        re.compile(r"^https:\/\/localhost:\d+$"),
        re.compile(r"^http:\/\/192\.168\.\d{1,3}\.\d{1,3}:\d+$"),
        re.compile(r"^https:\/\/192\.168\.\d{1,3}\.\d{1,3}:\d+$"),
    ]

    # password
    PASSWORD_MIN_LENGTH: int = 4
    PASSWORD_UPPERCASE_REQUIRED: bool = False
    PASSWORD_LOWERCASE_REQUIRED: bool = False
    PASSWORD_DIGIT_REQUIRED: bool = True
    PASSWORD_ALPHABETIC_REQUIRED: bool = True
    PASSWORD_SPECIAL_CHARACTERS_REQUIRED: bool = False
    PASSWORD_SPECIAL_CHARACTERS: str = r"[!@#$%^&*()]"

    # postgres
    POSTGRES_DRIVER: str = "postgresql"
    POSTGRES_ASYNC_DRIVER: str = "postgresql+asyncpg"
    POSTGRES_SYNC_DRIVER: str = "postgresql+psycopg"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_SLAVE_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"

    def _build_uri(self, driver: str, host: str) -> str:
        """ساخت URI اتصال به دیتابیس"""
        return f"{driver}://{self.POSTGRES_USER}:{quote(self.POSTGRES_PASSWORD)}@{host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_URI(self) -> str:
        """اتصال همگام به Master"""
        return self._build_uri(self.POSTGRES_DRIVER, self.POSTGRES_HOST)

    @property
    def POSTGRES_ASYNC_URI(self) -> str:
        """اتصال ناهمگام به Master"""
        return self._build_uri(self.POSTGRES_ASYNC_DRIVER, self.POSTGRES_HOST)

    @property
    def POSTGRES_SYNC_URI(self) -> str:
        """اتصال همگام به Master"""
        return self._build_uri(self.POSTGRES_SYNC_DRIVER, self.POSTGRES_HOST)

    @property
    def POSTGRES_ASYNC_SLAVE_URI(self) -> str:
        """اتصال ناهمگام به Replica"""
        return self._build_uri(self.POSTGRES_ASYNC_DRIVER, self.POSTGRES_SLAVE_HOST)

    # s3
    S3_ENDPOINT: str = "localhost"
    S3_api_ENDPOINT: str = S3_ENDPOINT
    S3_BUCKET_NAME: str = "university"
    S3_ACCESS_KEY: str = "minio"
    S3_SECRET_KEY: str = "minio123"

    KEYCLOAK_REAL_NAME: str = "university"
    KEYCLOAK_SERVER_URL: str = "localhost:8080"

    KEYCLOAK_CLIENT_ID: str = "client-id"
    KEYCLOAK_CLIENT_NAME: str = "client-id"
    KEYCLOAK_CLIENT_SECRET_KEY: str = "client-secret"

    KEYCLOAK_ADMIN_USER: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin-password"

    QR_SECRET_KEY: str = ""
    QR_VALID_TIME_SEC: int = 15

    # REDIS CONFIGS
    REDIS_HOST: str = "localhost"
    REDIS_DB: str = "0"
    REDIS_PORT: int = 6379
    REDIS_USER: str = "default"
    REDIS_PASSWORD: str = "default"
    REDIS_ENCODING: str = "utf-8"
    REDIS_RESPONSE_DECODE: bool = True

    @property
    def REDIS_URI(self) -> str:
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    KAFKA_ADDRESS: str = ""
    KAFKA_SEND_NOTIFICATION: str = "SEND_NOTIFICATION"

    KAVENEGAR_ACCESS_KEY: str = ""
    KAVENEGAR_SENDER: str = ""

    # rc
    RC_BASE_URL: str = "https://chat.timez.ir"
    RC_MONGO_HOST: str = ""
    RC_MONGO_PASSWORD: str = ""
    RC_MONGO_USERNAME: str = ""

    # mongodb
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = "timez"
    MONGODB_USER: str = "timez"
    MONGODB_PASSWORD: str = "timez"

    FACE_BASE_URL: str = "https://face.m.timez.ir"
    PISHGAMRAYAN_API_KEY: str = ""
    limit_features: bool = False
    limit_urls: str = ""

    USE_SLAVE: bool = False

    ENVIRONMENT: str | None = None

    TORTOISE_MODELS: list[str] = [
        "backbone.adapters.auth_adapter",
        "backbone.data_models.user",
    ]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_EXPIRE_SECONDS: int = 120
    TOKEN_EXPIRE_MINUTES: int = 28800
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 57600

    SMS_API_KEY: str = ""
    SMS_SENDER: str = "2000660110"


configs = Configs()


# Tortoise ORM config — kept for potential future use alongside SQLAlchemy.
TORTOISE_ORM: dict = {
    "connections": {
        configs.POSTGRES_DB: configs.POSTGRES_URI,
    },
    "apps": {
        "models": {
            "models": configs.TORTOISE_MODELS,
            "default_connection": configs.POSTGRES_DB,
        },
    },
}
