from datetime import datetime
from fastapi import APIRouter
from pydantic import Field, field_validator
from backbone.adapters.sms_adapter_kavenegar import SMSAdapter
from backbone.adapters.tortoise_adapter import TortoiseAdapter
from backbone.configs import Configs
from backbone.exceptions import (
    Exception400OTPExpired,
    Exception404,
    Exception404OTPNotRequested,
    Exception503SMS,
)
from backbone.mixins.pydantic import (
    PydanticMixinContact,
    PydanticMixinPhoneRequired,
    PydanticMixinTokenRequired,
    PydanticMixinUserID,
    PydanticMixinUsernameRequired,
)
from bootstrap.setup_locator import loc
from backbone.adapters.auth_adapter import AuthAdapter, LoginEx
from backbone.bases.base_request import BaseRequest, BaseResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


class OTPRequest(BaseRequest, PydanticMixinPhoneRequired):
    pass


class OTPResponse(BaseResponse):
    digits: int
    time: datetime


@router.post("/otp", response_model=OTPResponse)
async def otp(request: OTPRequest):
    authAdapter: AuthAdapter = loc.get("AuthAdapter")
    cfg: Configs = loc.get("Configs")
    userOrEx = await authAdapter.get_user(phone=request.phone)
    if isinstance(userOrEx, LoginEx):
        raise Exception404()

    tortoiseAdapter: TortoiseAdapter = loc.get("TortoiseAdapter")
    async with tortoiseAdapter.transaction():
        otpOrEx = await authAdapter.generate_otp(userOrEx.user_id)

    if isinstance(otpOrEx, LoginEx):
        raise Exception400OTPExpired()
    sms: SMSAdapter = loc.get("SMSAdapter")
    send = await sms.send_sms(request.phone, str(otpOrEx[0]))
    if not (send):
        raise Exception503SMS()

    return OTPResponse(time=otpOrEx[1], digits=cfg.OTP_LENGTH)


class VerifyOTPRequest(BaseRequest, PydanticMixinPhoneRequired):
    code: int = Field(  # type: ignore
        ...,
        description="OTP CODE",
        example=123456,
    )


class VerifyOTPResponse(
    BaseResponse,
    PydanticMixinUserID,
    PydanticMixinUsernameRequired,
    PydanticMixinContact,
    PydanticMixinTokenRequired,
):
    pass


@router.post("/verify_otp", response_model=VerifyOTPResponse)
async def verifyOtp(request: VerifyOTPRequest):
    authAdapter: AuthAdapter = loc.get("AuthAdapter")
    userOrEx = await authAdapter.get_user(phone=request.phone)
    if isinstance(userOrEx, LoginEx):
        raise Exception404OTPNotRequested()
    tokensOrEx = await authAdapter.verify_otp(userOrEx.user_id, request.code)
    if isinstance(tokensOrEx, LoginEx):
        raise Exception400OTPExpired()
    return VerifyOTPResponse(
        email=userOrEx.email,
        phone=userOrEx.phone,
        user_id=userOrEx.user_id,
        username=userOrEx.username,
        token=tokensOrEx[0],
        refresh_token=tokensOrEx[1],
    )
