from datetime import date

from backbone.adapters.async_auth_adapter import AsyncRedisAuthAdapter
from backbone.adapters.file_storage_service import FileStorageService
from backbone.bases.base_request import BaseRequest, BaseResponse
from backbone.db.db_enums import (
    LanguageTypeEnum as LanguageTypeEnumTable,
)
from backbone.db.db_enums import (
    ThemeTypeEnum as ThemeTypeEnumTable,
)
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.db.tables import User, UserSettings
from backbone.db_enums_generated import (
    LanguageTypeEnum as LanguageChoice,
)
from backbone.db_enums_generated import (
    ThemeTypeEnum as ThemeChoice,
)
from backbone.exceptions import (
    Exception400,
    Exception400AlreadyExist,
    Exception404,
)
from backbone.helpers.more_funcs import get_current_user_id
from backbone.mixins.pydantic import (
    PydanticMixinContact,
    PydanticMixinUserID,
)
from bootstrap.locator import loc
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/users", tags=["user"])


# =========================================================
# Profile (/user/me)
# =========================================================


class UserMeResponse(
    BaseResponse,
    PydanticMixinUserID,
    PydanticMixinContact,
):
    name: str | None = Field(None, description="نام کاربر")
    given_name: str | None = Field(None, description="نام کوچک کاربر")
    email: EmailStr | None = Field(None, description="ایمیل کاربر")
    birthday: date | None = Field(None, description="تاریخ تولد کاربر")
    is_profile_completed: bool = Field(..., description="آیا پروفایل تکمیل شده است")
    profile_image: str | None = Field(None, description="آدرس تصویر پروفایل")


@router.get("/me", response_model=UserMeResponse)
async def get_me(request: Request):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise Exception404()

        return UserMeResponse(
            user_id=user.id,
            phone=user.phone,
            email=user.email,
            name=user.name,
            given_name=user.given_name,
            birthday=user.birthday,
            is_profile_completed=user.is_profile_completed,
            profile_image=user.profile_image,
        )


class UpdateMeRequest(BaseRequest):
    name: str | None = None
    given_name: str | None = None
    email: EmailStr | None = None
    birthday: date | None = None
    profile_image: UploadFile | None = None

    @classmethod
    def as_form(
        cls,
        name: str | None = Form(None),
        given_name: str | None = Form(None),
        email: EmailStr | None = Form(None),
        birthday: date | None = Form(None),
        profile_image: UploadFile | None = File(None),
    ):
        return cls(
            name=name,
            given_name=given_name,
            email=email,
            birthday=birthday,
            profile_image=profile_image,
        )


@router.put("/me", response_model=UserMeResponse)
async def update_me(
    request: Request,
    body: UpdateMeRequest = Depends(UpdateMeRequest.as_form),
):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")

    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.transaction() as session:

        result = await session.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if user is None:
            raise Exception404()

        # =========================
        # Email
        # =========================

        if body.email is not None and body.email != user.email:

            existing = await session.execute(
                select(User).where(User.email == body.email)
            )

            if existing.scalar_one_or_none():
                raise Exception400AlreadyExist(detail="این ایمیل قبلا ثبت شده است")

            user.email = body.email

        # =========================
        # Name
        # =========================

        if body.name is not None:
            user.name = body.name

        # =========================
        # Given Name
        # =========================

        if body.given_name is not None:
            user.given_name = body.given_name

        # =========================
        # Birthday
        # =========================

        if body.birthday is not None:
            user.birthday = body.birthday

        # =========================
        # Profile Image
        # =========================

        if body.profile_image is not None:

            profile_image = body.profile_image

            fileStorageService: FileStorageService = loc.get("FileStorageService")

            url = fileStorageService.save(
                file=profile_image.file,
                folder="profiles",
                filename=f"{user.id}_{profile_image.filename}",
            )

            user.profile_image = url

        # =========================
        # Profile Completion
        # =========================

        if (
            not user.is_profile_completed
            and user.profile_image
            and user.name
            and user.given_name
            and user.birthday
        ):
            user.is_profile_completed = True

        await session.flush()

        return UserMeResponse(
            user_id=user.id,
            phone=user.phone,
            email=user.email,
            name=user.name,
            given_name=user.given_name,
            birthday=user.birthday,
            is_profile_completed=user.is_profile_completed,
            profile_image=user.profile_image,
        )


# =========================================================
# Settings (/user/settings)
# =========================================================


class UserSettingsResponse(BaseResponse):
    theme: str | None = Field(None, description="تم انتخابی کاربر")
    language: str | None = Field(None, description="زبان انتخابی کاربر")
    enable_notifications: bool = Field(..., description="فعال بودن نوتیفیکیشن‌ها")
    extra_settings: dict | None = Field(None, description="سایر تنظیمات آزاد")


async def _get_settings_or_404(session, user_id: int) -> UserSettings:

    result = await session.execute(
        select(UserSettings)
        .options(
            selectinload(UserSettings.theme),
            selectinload(UserSettings.language),
        )
        .where(UserSettings.user_id == user_id)
    )

    settings = result.scalar_one_or_none()

    if settings is None:
        raise Exception404(detail="تنظیماتی برای این کاربر ثبت نشده است")

    return settings


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(request: Request):
    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:
        settings = await _get_settings_or_404(session, user_id)
        return UserSettingsResponse(
            theme=settings.theme.value if settings.theme else None,
            language=settings.language.value if settings.language else None,
            enable_notifications=settings.enable_notifications,
            extra_settings=settings.extra_settings,
        )


class UpdateSettingsRequest(BaseRequest):
    theme: ThemeChoice | None = Field(None, description="تم (dark/light/system)")
    language: LanguageChoice | None = Field(None, description="زبان (fa/en/ar)")
    enable_notifications: bool | None = Field(None, description="فعال/غیرفعال نوتیف")
    extra_settings: dict | None = Field(None, description="جایگزینی کامل تنظیمات آزاد")


@router.patch("/settings", response_model=UserSettingsResponse)
async def update_settings(request: Request, body: UpdateSettingsRequest):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.transaction() as session:

        settings = await _get_settings_or_404(session, user_id)

        if body.theme is not None:

            theme_row = await session.execute(
                select(ThemeTypeEnumTable).where(
                    ThemeTypeEnumTable.value == body.theme.value
                )
            )
            theme_row = theme_row.scalar_one_or_none()

            if theme_row is None:
                raise Exception400(detail="مقدار تم نامعتبر است")

            settings.theme_id = theme_row.id

        if body.language is not None:

            language_row = await session.execute(
                select(LanguageTypeEnumTable).where(
                    LanguageTypeEnumTable.value == body.language.value
                )
            )
            language_row = language_row.scalar_one_or_none()

            if language_row is None:
                raise Exception400(detail="مقدار زبان نامعتبر است")

            settings.language_id = language_row.id

        if body.enable_notifications is not None:
            settings.enable_notifications = body.enable_notifications

        if body.extra_settings is not None:
            settings.extra_settings = body.extra_settings

        await session.flush()

        settings = await _get_settings_or_404(session, user_id)

        return UserSettingsResponse(
            theme=settings.theme.value if settings.theme else None,
            language=settings.language.value if settings.language else None,
            enable_notifications=settings.enable_notifications,
            extra_settings=settings.extra_settings,
        )


# =========================================================
# Permissions (/user/permissions)
# =========================================================


class PermissionItem(BaseResponse):
    title: str = Field(..., description="عنوان دسترسی")
    value: str = Field(..., description="مقدار دسترسی")


@router.get("/permissions", response_model=list[PermissionItem])
async def get_my_permissions(request: Request):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        result = await session.execute(
            select(User)
            .options(selectinload(User.permissions))
            .where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise Exception404()

        return [PermissionItem(title=p.title, value=p.value) for p in user.permissions]


# =========================================================
# Sessions (/user/sessions) و Logout
# =========================================================


class SessionItem(BaseResponse):
    session_id: str = Field(..., description="شناسه نشست")
    created_at: str = Field(..., description="زمان ایجاد نشست")
    device_metadata: dict = Field(..., description="اطلاعات دستگاه")
    is_current: bool = Field(..., description="نشست جاری است یا خیر")


@router.get("/sessions", response_model=list[SessionItem])
async def get_my_sessions(request: Request):

    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")
    user_id = get_current_user_id(request)
    current_session_id = request.state.user.get("session_id")

    info = await asyncRedisAuthAdapter.get_info_by_user_id(str(user_id))

    return [
        SessionItem(
            session_id=s["session_id"],
            created_at=s["created_at"],
            device_metadata=s.get("device_metadata", {}),
            is_current=(s["session_id"] == current_session_id),
        )
        for s in info["sessions"]
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(request: Request, session_id: str):

    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")
    user_id = get_current_user_id(request)

    info = await asyncRedisAuthAdapter.get_info_by_user_id(str(user_id))

    target = next((s for s in info["sessions"] if s["session_id"] == session_id), None)

    if target is None:
        raise Exception404(detail="نشست مورد نظر یافت نشد")

    await asyncRedisAuthAdapter.revoke_session(target["access_token"])

    return {"status": "ok"}


@router.delete("/sessions")
async def revoke_all_sessions(request: Request):
    """خروج از تمام دستگاه‌ها (شامل نشست فعلی)"""

    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")
    user_id = get_current_user_id(request)

    info = await asyncRedisAuthAdapter.get_info_by_user_id(str(user_id))

    for s in info["sessions"]:
        await asyncRedisAuthAdapter.revoke_session(s["access_token"])

    return {"status": "ok", "revoked_count": len(info["sessions"])}


@router.post("/logout")
async def logout(request: Request):
    """خروج فقط از نشست فعلی"""

    asyncRedisAuthAdapter: AsyncRedisAuthAdapter = loc.get("AsyncRedisAuthAdapter")

    await asyncRedisAuthAdapter.revoke_session(request.state.user["access_token"])

    return {"status": "ok"}
