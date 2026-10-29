from datetime import date

from backbone.adapters.async_auth_adapter import AsyncRedisAuthAdapter
from backbone.bases.base_request import BaseRequest, BaseResponse
from backbone.configs import Configs
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.db.tables import User
from backbone.exceptions import (
    Exception400OTPExpired,
    Exception401ExpiredToken,
    Exception404OTPNotRequested,
)
from backbone.mixins.pydantic import (
    PydanticMixinContact,
    PydanticMixinPhoneRequired,
    PydanticMixinTokenRequired,
    PydanticMixinUserID,
)
from bootstrap.locator import loc
from fastapi import APIRouter
from pydantic import EmailStr, Field
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["Authentication", "public"])


class OTPRequest(BaseRequest, PydanticMixinPhoneRequired):
    pass


class OTPResponse(BaseResponse):
    digits: int
    timestamp: float


@router.post(
    "/otp",
    response_model=OTPResponse,
    tags=["public"],
)
async def otp(request: OTPRequest):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")

    cfg: Configs = loc.get("Configs")

    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")

    # sms: SMSAdapter = loc.get("SMSAdapter")

    async with sqlAlchemyAdapter.transaction() as session:
        result = await session.execute(select(User).where(User.phone == request.phone))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(phone=request.phone, is_profile_completed=False)
            session.add(user)
            await session.flush()

        otp_code, expires_at = await asyncRedisAuthAdapter.generate_otp(
            user_id=str(user.id)
        )
        # send = await sms.send_sms(
        #     request.phone,
        #     str(otp_code),
        # )

        # if not send:
        #     raise Exception503SMS()

        return OTPResponse(
            timestamp=expires_at.timestamp(),
            digits=cfg.OTP_LENGTH,
        )


class VerifyOTPRequest(BaseRequest, PydanticMixinPhoneRequired):
    code: int = Field(  # type: ignore
        ...,
        description="OTP CODE",
        example="".join([str(x) for x in range(6)]),
    )


class VerifyOTPResponse(
    BaseResponse,
    PydanticMixinUserID,
    PydanticMixinContact,
    PydanticMixinTokenRequired,
):
    name: str | None = Field(
        None,
        description="نام کاربر",
    )

    given_name: str | None = Field(
        None,
        description="نام کوچک کاربر",
    )

    email: EmailStr | None = Field(
        None,
        description="ایمیل کاربر",
    )

    birthday: date | None = Field(
        None,
        description="تاریخ تولد کاربر",
    )

    is_profile_completed: bool = Field(
        ...,
        description="آیا پروفایل کاربر تکمیل شده است",
    )

    profile_image: str | None = Field(
        None,
        description="آدرس تصویر پروفایل کاربر",
    )


@router.post("/verify_otp", response_model=VerifyOTPResponse)
async def verifyOtp(request: VerifyOTPRequest):
    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")

    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")
    async with sqlAlchemyAdapter.transaction() as session:
        result = await session.execute(select(User).where(User.phone == request.phone))
        user = result.scalar_one_or_none()

        if user is None:
            raise Exception404OTPNotRequested()
        tokens = await asyncRedisAuthAdapter.verify_otp_and_generate_tokens(
            user_id=user.id, input_otp=str(request.code), device_metadata={}
        )

        if not tokens:
            raise Exception400OTPExpired()

        return VerifyOTPResponse(
            email=user.email,
            phone=user.phone,
            user_id=user.id,
            token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            name=user.name,
            birthday=user.birthday,
            is_profile_completed=user.is_profile_completed,
            given_name=user.given_name,
            profile_image=user.profile_image,
        )


# backbone/routes/auth.py (یا فایل مربوط به روت‌های auth)


class RefreshTokenRequest(BaseRequest):
    """
    درخواست رفرش توکن
    فیلد token یا refresh_token از طریق PydanticMixinTokenRequired یا Field دریافت می‌شود.
    """

    refresh_token: str = Field(
        ...,
        description="JWT refresh token string, optionally prefixed with Bearer",
        pattern=(r"^(?:Bearer\s+)?" r"[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$"),
        json_schema_extra={
            "examples": [
                (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                    "eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCJ9."
                    "8Vci6xB_1up3khVzKJcUSZrB1vVEt3tX9N1x3m8NzkM"
                ),
                (
                    "Bearer "
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                    "eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCJ9."
                    "8Vci6xB_1up3khVzKJcUSZrB1vVEt3tX9N1x3m8NzkM"
                ),
            ],
        },
    )


class RefreshTokenResponse(BaseResponse):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    tags=["public"],
    summary="تنگدید توکن دسترسی (Refresh Token)",
)
async def refresh_token(request: RefreshTokenRequest):
    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")

    # ۱. اعتبارسنجی و بررسی صحت توکن رفرش از طریق Adapter / Redis
    tokens = await asyncRedisAuthAdapter.refresh_access_token(request.refresh_token)
    if not tokens:
        raise Exception401ExpiredToken()  # یا Exception401Unauthorized

    return RefreshTokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )
