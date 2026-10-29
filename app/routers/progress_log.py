from datetime import datetime
from typing import Annotated

from backbone.bases.base_request import BaseRequest, BaseResponse
from backbone.db.db_enums import UserMetricTypeEnum as UserMetricTypeEnumTable
from backbone.db.sqlalchemy_db_based import SQLAlchemyAdapter
from backbone.db.tables import UserProgressLog
from backbone.db_enums_generated import UserMetricTypeEnum as MetricChoice
from backbone.exceptions import Exception400
from backbone.helpers.more_funcs import get_current_user_id
from backbone.mixins.pydantic import PydanticMixinPagination
from bootstrap.locator import loc
from fastapi import APIRouter, Depends, Query, Request
from pydantic import Field
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/user/progress-logs", tags=["user", "progress-log"])


class ProgressLogItem(BaseResponse):
    id: int
    metric_type: str = Field(..., description="عنوان متریک (title)")
    value: float
    notes: str | None = None
    created_at: datetime


class ProgressLogListResponse(BaseResponse, PydanticMixinPagination):
    total: int = Field(..., description="تعداد کل رکوردها")
    items: list[ProgressLogItem]


@router.get("", response_model=ProgressLogListResponse)
async def get_progress_logs(
    request: Request,
    pagination: Annotated[PydanticMixinPagination, Depends()],
    metric_type: MetricChoice | None = Query(
        None, description="فیلتر بر اساس نوع متریک"
    ),
):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:

        base_stmt = select(UserProgressLog).where(UserProgressLog.user_id == user_id)
        count_stmt = select(func.count(UserProgressLog.id)).where(
            UserProgressLog.user_id == user_id
        )

        if metric_type is not None:
            base_stmt = base_stmt.join(UserProgressLog.metric_type_enum).where(
                UserMetricTypeEnumTable.title == metric_type.name
            )
            count_stmt = count_stmt.join(UserProgressLog.metric_type_enum).where(
                UserMetricTypeEnumTable.title == metric_type.name
            )

        total = (await session.execute(count_stmt)).scalar_one()

        stmt = (
            base_stmt.options(selectinload(UserProgressLog.metric_type_enum))
            .order_by(UserProgressLog.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        result = await session.execute(stmt)
        logs = result.scalars().all()

        return ProgressLogListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            items=[
                ProgressLogItem(
                    id=log.id,
                    metric_type=log.metric_type_enum.title,
                    value=log.value,
                    notes=log.notes,
                    created_at=log.created_at,
                )
                for log in logs
            ],
        )


class CreateProgressLogRequest(BaseRequest):
    metric_type: MetricChoice = Field(..., description="نوع متریک")
    value: float = Field(..., description="مقدار ثبت‌شده")
    notes: str | None = Field(None, description="یادداشت اختیاری")


@router.post("", response_model=ProgressLogItem)
async def create_progress_log(request: Request, body: CreateProgressLogRequest):

    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.transaction() as session:

        metric_row = await session.execute(
            select(UserMetricTypeEnumTable).where(
                UserMetricTypeEnumTable.title == body.metric_type.name
            )
        )
        metric_row = metric_row.scalar_one_or_none()

        if metric_row is None:
            raise Exception400(detail="نوع متریک نامعتبر است")

        log = UserProgressLog(
            user_id=user_id,
            metric_type_enum_id=metric_row.id,
            value=body.value,
            notes=body.notes,
        )

        session.add(log)
        await session.flush()

        return ProgressLogItem(
            id=log.id,
            metric_type=metric_row.title,
            value=log.value,
            notes=log.notes,
            created_at=log.created_at,
        )
