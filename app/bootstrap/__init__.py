from backbone.adapters.seeders.user import user_seeders
from bootstrap.setup_locator import setup_locator


async def setup_app():
    await setup_locator()
