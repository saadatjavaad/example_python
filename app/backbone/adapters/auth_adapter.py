# ابتدا باید ادرس این فایل به tortoiseAdapter معرقی شود چون این مدل شخصی دارد برای ساخت جدول
# نکته بعد اینه که ما هم میتونیم از متد های انی کلاس بصورت عادی استفاده کنیم و هم در tortoiseAdapter.transaction و در دو حالت متد ها قابل استفاده است
import logging
import random
import jwt
from enum import Enum
import hashlib
import hmac
from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from backbone.mixins.tortoise import (
    TortoiseMixinBase,
    TortoiseMixinContactAtLeastOne,
    TortoiseMixinOtp,
    TortoiseMixinPass,
    TortoiseMixinToken,
    TortoiseMixinUserId,
    TortoiseMixinUserUsername,
)


class UserAuthDataModel(
    TortoiseMixinBase,
    TortoiseMixinUserId,
    TortoiseMixinUserUsername,
    TortoiseMixinPass,
    TortoiseMixinContactAtLeastOne,
    TortoiseMixinToken,
    TortoiseMixinOtp,
):

    class Meta:
        constraints = ["CHECK (phone IS NOT NULL OR email IS NOT NULL)"]
        indexes = ("username", "email", "phone")


@dataclass
class UserAuthAdapterDTO:
    user_id: int
    username: str
    password: str
    phone: str
    email: str
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    otp: Optional[int] = None
    otp_exp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class LoginEx(Enum):
    UserNotFound = "UserNotFound"
    PasswordNotTrue = "PasswordNotTrue"
    PasswordIsEmpty = "PasswordIsEmpty"
    TokenExpired = "TokenExpired"
    OTPExpired = "OTPExpired"


@dataclass
class AuthAdapterConfig:
    token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 3000
    secret_key: str = "saadatjavaad"
    otp_digits: int = 6
    otp_expire_minutes: int = 10000


class AuthAdapter:
    def __init__(self, cfg: AuthAdapterConfig):
        self.cfg = cfg

    @staticmethod
    def _hash_pass(p: str) -> str:
        return hashlib.sha256(p.encode()).hexdigest()

    @staticmethod
    def _user_data_model_to_dto(dm) -> UserAuthAdapterDTO:
        return UserAuthAdapterDTO(
            user_id=dm.user_id,
            username=dm.username,
            password=dm.password,
            phone=dm.phone,
            email=dm.email,
            token=dm.token,
            refresh_token=dm.refresh_token,
            otp=dm.otp,
            otp_exp=dm.otp_exp,
            created_at=dm.created_at,
            deleted_at=dm.deleted_at,
            updated_at=dm.updated_at,
        )

    async def _create_tokens(self, user: UserAuthDataModel) -> Tuple[str, str]:
        """ایجاد access و refresh توکن"""

        now = datetime.utcnow()

        access_payload = {
            "user_id": user.user_id,
            "username": user.username,
            "exp": now + timedelta(minutes=self.cfg.token_expire_minutes),
        }
        refresh_payload = {
            "user_id": user.user_id,
            "exp": now + timedelta(minutes=self.cfg.refresh_token_expire_minutes),
        }

        access_token = jwt.encode(
            access_payload, self.cfg.secret_key, algorithm="HS256"
        )
        refresh_token = jwt.encode(
            refresh_payload, self.cfg.secret_key, algorithm="HS256"
        )

        user.token = access_token
        user.refresh_token = refresh_token
        await user.save()

        return access_token, refresh_token

    async def create_user(self, user: UserAuthAdapterDTO):
        hashed_password = ""
        if user.password:
            hashed_password = self._hash_pass(user.password)
        await UserAuthDataModel.create(
            user_id=user.user_id,
            username=user.username,
            password=hashed_password,
            phone=user.phone,
            email=user.email,
        )

    async def login(self, username: str, password: str) -> LoginEx | Tuple[str, str]:
        user = await UserAuthDataModel.get_or_none(username=username)
        if not user:
            return LoginEx.UserNotFound
        if not user.password:
            return LoginEx.PasswordIsEmpty
        hashed_input = self._hash_pass(password)
        if not hmac.compare_digest(user.password, hashed_input):
            return LoginEx.PasswordNotTrue
        access_token, refresh_token = await self._create_tokens(user)
        return access_token, refresh_token

    async def refresh_access_token(
        self, refresh_token: str
    ) -> LoginEx | Tuple[str, str]:
        """ساخت access token جدید با refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, self.cfg.secret_key, algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            if not user_id:
                return LoginEx.UserNotFound
        except jwt.ExpiredSignatureError:
            logging.warning("Refresh token expired")
            return LoginEx.TokenExpired
        except jwt.InvalidTokenError:
            logging.warning("Invalid refresh token")
            return LoginEx.TokenExpired

        user = await UserAuthDataModel.get_or_none(user_id=user_id)
        if not user:
            return LoginEx.UserNotFound
        if getattr(user_id, "refresh_token", None) != refresh_token:
            return LoginEx.TokenExpired

        return await self._create_tokens(user_id)

    async def get_user_by_token(self, token: str) -> LoginEx | UserAuthAdapterDTO:
        """
        همچنین برای بررسی صحت توکن
        """
        try:
            payload = jwt.decode(token, self.cfg.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                return LoginEx.TokenExpired
        except jwt.ExpiredSignatureError:
            logging.warning("Token expired")
            return LoginEx.TokenExpired
        except jwt.InvalidTokenError:
            logging.warning("Invalid token")
            return LoginEx.TokenExpired

        userOrEx = await self.get_user(user_id=user_id)
        if isinstance(userOrEx, LoginEx):
            return userOrEx
        dto = self._user_data_model_to_dto(userOrEx)
        return dto

    async def generate_otp(self, user_id: int) -> LoginEx | Tuple[int, datetime]:
        user = await UserAuthDataModel.get_or_none(user_id=user_id)
        if not user:
            return LoginEx.UserNotFound
        if self.cfg.otp_digits <= 0:
            raise ValueError("تعداد رقم باید بزرگ‌تر از صفر باشد.")
        start = 10 ** (self.cfg.otp_digits - 1)
        end = (10**self.cfg.otp_digits) - 1
        otp_code = random.randint(start, end)
        otp_exp = datetime.utcnow() + timedelta(minutes=self.cfg.otp_expire_minutes)
        user.update_from_dict({"otp": otp_code, "otp_exp": otp_exp})
        await user.save()
        return (otp_code, otp_exp)

    async def verify_otp(self, user_id: int, otp: int) -> LoginEx | Tuple[str, str]:
        user = await UserAuthDataModel.get_or_none(user_id=user_id)
        if not user:
            return LoginEx.UserNotFound
        if not user.otp or not user.otp_exp:
            return LoginEx.OTPExpired

        if datetime.now(timezone.utc) > user.otp_exp.astimezone(timezone.utc):
            return LoginEx.OTPExpired

        if user.otp != otp:
            return LoginEx.OTPExpired
        return await self._create_tokens(user)

    async def get_user(self, **kw) -> LoginEx | UserAuthAdapterDTO:
        """
        get_user(username:"saadatjavaad")

        """
        user = await UserAuthDataModel.get_or_none(**kw)

        if not user:
            return LoginEx.UserNotFound
        return self._user_data_model_to_dto(user)
