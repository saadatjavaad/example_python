from datetime import datetime, timezone
from typing import Annotated

from backbone.bases.base_request import BaseResponse
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.db.tables import NotificationRecipient
from backbone.exceptions import Exception404
from backbone.helpers.more_funcs import get_current_user_id
from backbone.mixins.pydantic import PydanticMixinPagination
from bootstrap.locator import loc
from fastapi import APIRouter, Depends, Query, Request
from pydantic import Field
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/user/notifications", tags=["user", "notification"])


class NotificationItem(BaseResponse):
    notification_id: int
    title: str
    content: str
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime


class NotificationListResponse(BaseResponse, PydanticMixinPagination):
    total: int = Field(..., description="تعداد کل رکوردها")
    items: list[NotificationItem]


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    request: Request,
    pagination: Annotated[PydanticMixinPagination, Depends()],
    unread_only: bool = Query(False, description="فقط نوتیفیکیشن‌های خوانده‌نشده"),
):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        count_stmt = select(func.count(NotificationRecipient.id)).where(
            NotificationRecipient.recipient_id == user_id
        )

        stmt = (
            select(NotificationRecipient)
            .options(selectinload(NotificationRecipient.notification))
            .where(NotificationRecipient.recipient_id == user_id)
            .order_by(NotificationRecipient.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        if unread_only:
            count_stmt = count_stmt.where(NotificationRecipient.is_read.is_(False))
            stmt = stmt.where(NotificationRecipient.is_read.is_(False))

        total = (await session.execute(count_stmt)).scalar_one()

        result = await session.execute(stmt)
        items = result.scalars().all()

        return NotificationListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            items=[
                NotificationItem(
                    notification_id=item.notification_id,
                    title=item.notification.title,
                    content=item.notification.content,
                    is_read=item.is_read,
                    read_at=item.read_at,
                    created_at=item.created_at,
                )
                for item in items
            ],
        )


@router.get("/unread-count")
async def get_unread_notifications_count(request: Request):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        result = await session.execute(
            select(func.count(NotificationRecipient.id)).where(
                NotificationRecipient.recipient_id == user_id,
                NotificationRecipient.is_read.is_(False),
            )
        )

        return {"unread_count": result.scalar_one()}


@router.patch("/{notification_id}/read")
async def mark_notification_as_read(request: Request, notification_id: int):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.transaction() as session:

        result = await session.execute(
            select(NotificationRecipient).where(
                NotificationRecipient.notification_id == notification_id,
                NotificationRecipient.recipient_id == user_id,
            )
        )

        recipient = result.scalar_one_or_none()

        if recipient is None:
            raise Exception404(detail="نوتیفیکیشن یافت نشد")

        if not recipient.is_read:
            recipient.is_read = True
            recipient.read_at = datetime.now(timezone.utc)

        return {"status": "ok"}


@router.patch("/read-all")
async def mark_all_notifications_as_read(request: Request):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.transaction() as session:

        result = await session.execute(
            select(NotificationRecipient).where(
                NotificationRecipient.recipient_id == user_id,
                NotificationRecipient.is_read.is_(False),
            )
        )

        recipients = result.scalars().all()
        now = datetime.now(timezone.utc)

        for r in recipients:
            r.is_read = True
            r.read_at = now

        return {"status": "ok", "updated_count": len(recipients)}