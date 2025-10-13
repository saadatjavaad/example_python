from backbone.configs import configs as cfg
from backbone.adapters.tortoise_adapter import TortoiseAdapter, TortoiseAdapterConfig


async def init_tortoise():

    tortoiseAdapter = TortoiseAdapter(
        TortoiseAdapterConfig(
            db_url=cfg.POSTGRES_URI,
            models_packages=cfg.TORTOISE_MODELS,
        )
    )
    await tortoiseAdapter.init()
    return tortoiseAdapter
