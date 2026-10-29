from datetime import datetime
from typing import Annotated

from backbone.bases.base_request import BaseResponse
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.db.tables import UserGift
from backbone.helpers.more_funcs import get_current_user_id
from backbone.mixins.pydantic import PydanticMixinPagination
from bootstrap.locator import loc
from fastapi import APIRouter, Depends, Request
from pydantic import Field
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/user/gifts", tags=["user", "gift"])


class GiftItem(BaseResponse):
    id: int
    title: str
    description: str | None = None
    value: float | None = None
    is_gifted: bool
    gifted_at: datetime | None = None


class GiftListResponse(BaseResponse, PydanticMixinPagination):
    total: int = Field(..., description="تعداد کل رکوردها")
    items: list[GiftItem]


@router.get("", response_model=GiftListResponse)
async def get_my_gifts(
    request: Request,
    pagination: Annotated[PydanticMixinPagination, Depends()],
):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        total = (
            await session.execute(
                select(func.count(UserGift.id)).where(UserGift.user_id == user_id)
            )
        ).scalar_one()

        result = await session.execute(
            select(UserGift)
            .options(selectinload(UserGift.gift))
            .where(UserGift.user_id == user_id)
            .order_by(UserGift.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        user_gifts = result.scalars().all()

        return GiftListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            items=[
                GiftItem(
                    id=ug.id,
                    title=ug.gift.title,
                    description=ug.gift.description,
                    value=ug.gift.value,
                    is_gifted=ug.is_gifted,
                    gifted_at=ug.gifted_at,
                )
                for ug in user_gifts
            ],
        )
