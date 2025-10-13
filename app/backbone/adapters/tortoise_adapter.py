from dataclasses import dataclass
from tortoise import Tortoise  # type: ignore
from tortoise.transactions import in_transaction


@dataclass
class TortoiseAdapterConfig:
    """
    تنظیمات اتصال به دیتابیس و ماژول‌ها
    """

    db_url: str  # مثال: postgres://user:pass@localhost:5432/mydb
    models_packages: list[str]  # مسیر پکیج‌هایی که مدل‌ها در آن هستند
    app_label: str = "models"  # namespace دلخواه برای مدل‌ها


class TortoiseAdapter:
    def __init__(self, config: TortoiseAdapterConfig):
        self.config = config
        self.initialized = False

    async def init(self):
        if self.initialized:
            return

        await Tortoise.init(
            config={
                "connections": {self.config.app_label: self.config.db_url},
                "apps": {
                    self.config.app_label: {
                        "models": self.config.models_packages,
                        "default_connection": self.config.app_label,
                    }
                },
            }
        )
        self.initialized = True
        print(f"✅ Tortoise ORM initialized for '{self.config.app_label}'")

    async def close(self):
        await Tortoise.close_connections()
        print(f"🔒 Database connections for '{self.config.app_label}' closed")

    def transaction(self):
        if not self.initialized:
            raise RuntimeError(
                f"TortoiseAdapter '{self.config.app_label}' must be initialized before using transactions."
            )
        return in_transaction(self.config.app_label)


# if __name__ == "__main__":  نمونه استفاده مثلا از دو دیتا بیس در برنامه

#     async def main():
#         # آداپتر اول
#         config1 = TortoiseAdapterConfig(
#             db_url="postgres://user:pass@localhost:5432/db1",
#             models_packages=[
#                 "models.user"
#             ],  # ادرس فایل یا پوشه که دارای کلاس هایی است که نوع  کلاس های تورتویز است و از ان ارث بری کرده اند
#             app_label="users",
#         )
#         adapter1 = TortoiseAdapter(config1, connection_name="db1")
#         await adapter1.init()

#         # آداپتر دوم
#         config2 = TortoiseAdapterConfig(
#             db_url="postgres://user:pass@localhost:5432/db2",
#             models_packages=["models.logs"],
#             app_label="logs",
#         )
#         adapter2 = TortoiseAdapter(config2, connection_name="db2")
#         await adapter2.init()

#         # عملیات روی دیتابیس اول
#         async with adapter1.transaction():
#             await User.create(name="Ali", email="ali@example.com")

#         # عملیات روی دیتابیس دوم
#         async with adapter2.transaction():
#             await Log.create(action="create_user", user_id=1)

#     asyncio.run(main)

#  AERICH

# # tortoise_config.py
# TORTOISE_ORM = {
#     "connections": {
#         "db1": "postgres://user:pass@localhost:5432/db1",
#         "db2": "postgres://user:pass@localhost:5432/db2",
#     },
#     "apps": {
#         "users": {
#             "models": ["models.user"],
#             "default_connection": "db1",
#         },
#         "logs": {
#             "models": ["models.logs"],
#             "default_connection": "db2",
#         },
#     },
# }


# # برای دیتابیس کاربران
# aerich init -t tortoise_config.TORTOISE_ORM -a users -d migrations/users

# # برای دیتابیس لاگ‌ها
# aerich init -t tortoise_config.TORTOISE_ORM -a logs -d migrations/logs

# aerich init -t backbone.configs.TORTOISE_ORM
