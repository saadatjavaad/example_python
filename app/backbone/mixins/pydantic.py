from datetime import datetime
import re
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

# 📞 الگوها (Regex Patterns)


IRAN_PHONE_REGEX = re.compile(r"^(?:\+98|0)?9\d{9}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")  # فقط حروف، اعداد و _
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$")
# رمز باید حداقل 8 کاراکتر و شامل عدد و حرف باشد


class PydanticMixinPhoneRequired(BaseModel):
    phone: str = Field(
        ...,
        pattern=IRAN_PHONE_REGEX,
        description="Phone number of the user (Iran format)",
        json_schema_extra={"example": "+989123456789"},
    )

    @field_validator("phone")
    def normalize_phone(cls, v: str) -> str:
        v = v.strip()
        if not IRAN_PHONE_REGEX.match(v):
            raise ValueError("شماره موبایل معتبر نیست (فرمت ایران).")

        if v.startswith("0"):
            v = "+98" + v[1:]
        elif v.startswith("9"):
            v = "+98" + v
        elif v.startswith("98"):
            v = "+" + v
        return v


class PydanticMixinPhoneOptional(BaseModel):
    phone: str | None = Field(
        None,
        pattern=IRAN_PHONE_REGEX,
        description="Optional phone number (Iran format)",
        json_schema_extra={"example": "+989123456789"},
    )

    @field_validator("phone")
    def normalize_phone(cls, v: str | None) -> str | None:
        if not v:
            return v
        v = v.strip()
        if not IRAN_PHONE_REGEX.match(v):
            raise ValueError("شماره موبایل معتبر نیست (فرمت ایران).")
        if v.startswith("0"):
            v = "+98" + v[1:]
        elif v.startswith("9"):
            v = "+98" + v
        elif v.startswith("98"):
            v = "+" + v
        return v


class PydanticMixinUserID(BaseModel):
    user_id: int = Field(
        ...,
        description="user_id",
    )


class PydanticMixinEmailRequired(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Valid email address of the user",
        json_schema_extra={"example": "user@example.com"},
    )


class PydanticMixinEmailOptional(BaseModel):
    email: EmailStr | None = Field(
        None,
        description="Optional email address",
        json_schema_extra={"example": "user@example.com"},
    )


# 👤 کلاس‌های نام کاربری (username)


class PydanticMixinUsernameRequired(BaseModel):
    username: str = Field(
        ...,
        pattern=USERNAME_REGEX,
        description="Username (3-30 chars, only letters, numbers, underscore)",
        json_schema_extra={"example": "ali_reza123"},
    )

    @field_validator("username")
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "نام کاربری فقط می‌تواند شامل حروف، اعداد و _ باشد (۳ تا ۳۰ کاراکتر)."
            )
        return v


class PydanticMixinUsernameOptional(BaseModel):
    username: str | None = Field(
        None,
        pattern=USERNAME_REGEX,
        description="Optional username",
        json_schema_extra={"example": "ali_reza"},
    )

    @field_validator("username")
    def validate_username(cls, v: str | None) -> str | None:
        if not v:
            return v
        v = v.strip()
        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "نام کاربری فقط می‌تواند شامل حروف، اعداد و _ باشد (۳ تا ۳۰ کاراکتر)."
            )
        return v


class PydanticMixinPasswordRequired(BaseModel):
    password: str = Field(
        ...,
        pattern=PASSWORD_REGEX,
        description="Password must be at least 8 chars long and contain both letters and digits",
        json_schema_extra={"example": "abc12345"},
    )

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError("رمز عبور باید حداقل ۸ کاراکتر و شامل عدد و حرف باشد.")
        return v


class PydanticMixinPasswordOptional(BaseModel):
    password: str | None = Field(
        None,
        pattern=PASSWORD_REGEX,
        description="Optional password",
        json_schema_extra={"example": "abc12345"},
    )

    @field_validator("password")
    def validate_password(cls, v: str | None) -> str | None:
        if not v:
            return v
        if not PASSWORD_REGEX.match(v):
            raise ValueError("رمز عبور باید حداقل ۸ کاراکتر و شامل عدد و حرف باشد.")
        return v


# 📞📧 ترکیبی: حداقل یکی از phone یا email باید پر باشد


class PydanticMixinContact(BaseModel):
    phone: str | None = Field(
        None,
        pattern=IRAN_PHONE_REGEX,
        description="User phone number",
        json_schema_extra={"example": "+989123456789"},
    )
    email: EmailStr | None = Field(
        None,
        description="User email address",
        json_schema_extra={"example": "user@example.com"},
    )

    @model_validator(mode="after")
    def check_at_least_one(cls, values: Any) -> Any:
        if not values.phone and not values.email:
            raise ValueError("حداقل یکی از فیلدهای phone یا email باید پر باشد.")
        return values

    @field_validator("phone")
    def normalize_phone(cls, v: str | None) -> str | None:
        if not v:
            return v
        v = v.strip()
        if not IRAN_PHONE_REGEX.match(v):
            raise ValueError("شماره موبایل معتبر نیست (فرمت ایران).")
        if v.startswith("0"):
            v = "+98" + v[1:]
        elif v.startswith("9"):
            v = "+98" + v
        elif v.startswith("98"):
            v = "+" + v
        return v


class PydanticMixinTokenRequired(BaseModel):
    """
    Base model for JWT tokens including access and refresh tokens.
    Supports both raw JWT and Bearer JWT formats.
    """

    token: str = Field(
        ...,
        description="JWT access token string, optionally prefixed with Bearer",
        pattern=(r"^(?:Bearer\s+)?" r"[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$"),
        json_schema_extra={
            "examples": [
                (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                    "eyJ1c2VyX2lkIjoxLCJ0eXBlIjoiYWNjZXNzIn0."
                    "TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
                ),
                (
                    "Bearer "
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                    "eyJ1c2VyX2lkIjoxLCJ0eXBlIjoiYWNjZXNzIn0."
                    "TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
                ),
            ],
        },
    )

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


class PydanticMixinTokenOptional(BaseModel):
    """
    Optional version of PydanticMixinToken
    All fields are optional, but validation still applies if values are provided.
    """

    token: Optional[str] = Field(
        None,
        description="JWT access token string (optional)",
        pattern=r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$",
        json_schema_extra={
            "example": (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJ1c2VyX2lkIjoxLCJ0eXBlIjoiYWNjZXNzIn0."
                "TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
            ),
        },
    )

    refresh_token: Optional[str] = Field(
        None,
        description="JWT refresh token string (optional)",
        pattern=r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$",
        json_schema_extra={
            "example": (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCJ9."
                "8Vci6xB_1up3khVzKJcUSZrB1vVEt3tX9N1x3m8NzkM"
            ),
        },
    )

    # ✅ Validate JWT format (access token)
    @field_validator("token")
    @classmethod
    def validate_token_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        pattern = r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$"
        if not re.match(pattern, value):
            raise ValueError("Invalid access token format")
        return value

    # ✅ Validate JWT format (refresh token)
    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        pattern = r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$"
        if not re.match(pattern, value):
            raise ValueError("Invalid refresh token format")
        return value


class PydanticMixinOTP(BaseModel):
    """
    Model representing a One-Time Password (OTP) and its expiration.
    """

    otp: Optional[int] = Field(
        None,
        description="One-Time Password (OTP) numeric code",
        json_schema_extra={"example": 123456},
    )
    otp_exp: Optional[datetime] = Field(
        None,
        description="Expiration time for the OTP (UTC)",
        json_schema_extra={"example": "2025-10-12T20:00:00Z"},
    )

    otp_length: Optional[int] = Field(
        6,
        description=f"Expected length of the OTP code (default: {6} digits)",
        json_schema_extra={"example": 6},
    )

    # ✅ Validate OTP format (must match specified length)
    @field_validator("otp")
    @classmethod
    def validate_otp_length(cls, value: Optional[int], info) -> Optional[int]:
        if value is None:
            return value
        otp_length = info.data.get("otp_length", 6)
        if len(str(value)) != otp_length:
            raise ValueError(f"OTP must be exactly {otp_length} digits long")
        return value

    # ✅ Validate that OTP expiration is in the future
    @field_validator("otp_exp")
    @classmethod
    def validate_expiration(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value and value < datetime.utcnow():
            raise ValueError("OTP has already expired")
        return value


class PydanticMixinPagination(BaseModel):
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="تعداد رکورد در هر صفحه",
    )
    offset: int = Field(
        0,
        ge=0,
        description="تعداد رکورد رد شده از ابتدا",
    )
