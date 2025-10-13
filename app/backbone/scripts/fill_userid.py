import random
from backbone.adapters.auth_adapter import UserAuthDataModel
from backbone.adapters.tortoise_adapter import TortoiseAdapter
from bootstrap.setup_locator import loc


async def fill_user_ids():

    tortoiseAdapter: TortoiseAdapter = loc.get("TortoiseAdapter")

    async with tortoiseAdapter.transaction():
        users = await UserAuthDataModel.filter(user_id=None)
        for user in users:
            user.user_id = random.randint(100000, 999999)
            await user.save()
        print(f"{len(users)} old records fixed.")
