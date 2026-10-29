from backbone.adapters.auth_adapter import AuthAdapter, UserAuthAdapterDTO
from backbone.adapters.tortoise_adapter import TortoiseAdapter
from backbone.data_models.user import UserDataModel
from bootstrap.locator import loc


async def user_seeders():
    tortoiseAdapter: TortoiseAdapter = loc.get("TortoiseAdapter")
    authAdapter: AuthAdapter = loc.get("AuthAdapter")
    async with tortoiseAdapter.transaction():
        for i in range(10000):
            user: UserDataModel = await UserDataModel.create(
                username=f"user_{i}",
                email=f"user_{i}@gmail.com",
            )
            await authAdapter.create_user(
                UserAuthAdapterDTO(
                    user_id=user.id,
                    username=user.username,
                    phone=user.phone,
                    email=user.email,
                    password=user.email
                )
            )
