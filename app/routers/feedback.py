from datetime import datetime
from typing import Annotated

from backbone.bases.base_request import BaseRequest, BaseResponse
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.db.tables import User, UserFeedback
from backbone.exceptions import Exception400, Exception404
from backbone.helpers.more_funcs import get_current_user_id
from backbone.mixins.pydantic import PydanticMixinPagination
from bootstrap.locator import loc
from fastapi import APIRouter, Depends, Request
from pydantic import Field
from sqlalchemy import func, select

router = APIRouter(prefix="/user/feedbacks", tags=["user", "feedback"])


class FeedbackItem(BaseResponse):
    id: int
    title: str | None = None
    content: str
    is_anonymous: bool
    sender_id: int | None = Field(
        None, description="در صورت ناشناس بودن، null برگردانده می‌شود"
    )
    created_at: datetime


class FeedbackListResponse(BaseResponse, PydanticMixinPagination):
    total: int = Field(..., description="تعداد کل رکوردها")
    items: list[FeedbackItem]


@router.get("/received", response_model=FeedbackListResponse)
async def get_received_feedbacks(
    request: Request,
    pagination: Annotated[PydanticMixinPagination, Depends()],
):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        total = (
            await session.execute(
                select(func.count(UserFeedback.id)).where(
                    UserFeedback.recipient_id == user_id
                )
            )
        ).scalar_one()

        result = await session.execute(
            select(UserFeedback)
            .where(UserFeedback.recipient_id == user_id)
            .order_by(UserFeedback.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        feedbacks = result.scalars().all()

        return FeedbackListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            items=[
                FeedbackItem(
                    id=f.id,
                    title=f.title,
                    content=f.content,
                    is_anonymous=f.is_anonymous,
                    sender_id=None if f.is_anonymous else f.sender_id,
                    created_at=f.created_at,
                )
                for f in feedbacks
            ],
        )


@router.get("/sent", response_model=FeedbackListResponse)
async def get_sent_feedbacks(
    request: Request,
    pagination: Annotated[PydanticMixinPagination, Depends()],
):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        total = (
            await session.execute(
                select(func.count(UserFeedback.id)).where(
                    UserFeedback.sender_id == user_id
                )
            )
        ).scalar_one()

        result = await session.execute(
            select(UserFeedback)
            .where(UserFeedback.sender_id == user_id)
            .order_by(UserFeedback.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        feedbacks = result.scalars().all()

        return FeedbackListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            items=[
                FeedbackItem(
                    id=f.id,
                    title=f.title,
                    content=f.content,
                    is_anonymous=f.is_anonymous,
                    sender_id=f.sender_id,
                    created_at=f.created_at,
                )
                for f in feedbacks
            ],
        )


class CreateFeedbackRequest(BaseRequest):
    recipient_id: int = Field(..., description="شناسه کاربر گیرنده")
    title: str | None = Field(None, description="عنوان بازخورد")
    content: str = Field(..., min_length=1, max_length=1000, description="متن بازخورد")
    is_anonymous: bool = Field(False, description="آیا هویت فرستنده مخفی باشد")


@router.post("", response_model=FeedbackItem)
async def create_feedback(request: Request, body: CreateFeedbackRequest):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    if body.recipient_id == user_id:
        raise Exception400(detail="امکان ارسال بازخورد برای خودتان وجود ندارد")

    async with sqlAlchemyAdapter.transaction() as session:

        recipient_exists = await session.execute(
            select(User.id).where(User.id == body.recipient_id)
        )

        if recipient_exists.scalar_one_or_none() is None:
            raise Exception404(detail="کاربر گیرنده یافت نشد")

        feedback = UserFeedback(
            recipient_id=body.recipient_id,
            sender_id=user_id,
            title=body.title,
            content=body.content,
            is_anonymous=body.is_anonymous,
        )

        session.add(feedback)
        await session.flush()

        return FeedbackItem(
            id=feedback.id,
            title=feedback.title,
            content=feedback.content,
            is_anonymous=feedback.is_anonymous,
            sender_id=feedback.sender_id,
            created_at=feedback.created_at,
        )