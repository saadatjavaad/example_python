from backbone.adapters.auth_adapter import AuthAdapter, AuthAdapterConfig
from backbone.adapters.sms_adapter_kavenegar import SMSAdapter
from backbone.locator_service import LocatorService
from backbone.configs import configs as cfg
from bootstrap.tortoise import init_tortoise

loc = LocatorService()


async def setup_locator():
    loc.registerSingleton(
        "Configs",
        lambda: cfg,
    )
    await loc.registerSingletonAsync(
        "TortoiseAdapter",
        init_tortoise,
    )
    loc.registerSingletonLazy(
        "AuthAdapter",
        lambda: AuthAdapter(
            AuthAdapterConfig(
                secret_key=cfg.SECRET_KEY,
                otp_digits=cfg.OTP_LENGTH,
                otp_expire_minutes=cfg.OTP_EXPIRE_MINUTES,
                token_expire_minutes=cfg.TOKEN_EXPIRE_MINUTES,
                refresh_token_expire_minutes=cfg.REFRESH_TOKEN_EXPIRE_MINUTES,
            )
        ),
    )
    loc.registerSingletonLazy(
        "SMSAdapter", lambda: SMSAdapter(api_key=cfg.SMS_API_KEY, sender=cfg.SMS_SENDER)
    ),
