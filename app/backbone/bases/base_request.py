from pydantic import BaseModel


# -----------------------------
# Base class for all requests
# -----------------------------
class BaseRequest(BaseModel):
    """Base class for all request DTOs"""

    # model_config = {
    #     # به طور خودکار فاصله‌ها از رشته‌ها حذف شود
    #     "str_strip_whitespace": True,
    #     # فیلدهای اضافی غیرمجاز باشند
    #     "extra": "forbid",
    #     # مثال برای تولید JSON Schema
    #     "json_schema_extra": {"example": {}},
    # }

    # @field_validator("*", mode="before")
    # @classmethod
    # def empty_str_to_none(cls, v):
    #     """Convert empty strings to None before validation"""
    #     if isinstance(v, str) and not v.strip():
    #         return None
    #     return v


# -----------------------------
# Base class for all responses
# -----------------------------


class BaseResponse(BaseModel):
    """Standardized response wrapper for all API endpoints"""

    # message: Optional[str] = Field(
    #     "success computer",
    #     description="Optional message for user or developer",
    # )
    # data: Any = Field(
    #     None,
    #     description="Returned data payload (generic type)",
    # )

    # model_config = {"from_attributes": True, "json_schema_extra": {"example": {}}}
