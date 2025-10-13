from backbone.adapters.auth_adapter import AuthAdapter, UserAuthAdapterDTO
from backbone.adapters.tortoise_adapter import TortoiseAdapter
from backbone.devlog import devlog
from backbone.mixins.pydantic import (
    PydanticMixinContact,
    PydanticMixinEmailRequired,
    PydanticMixinPasswordOptional,
    PydanticMixinPasswordRequired,
    PydanticMixinPhoneRequired,
    PydanticMixinUserID,
    PydanticMixinUsernameRequired,
)
from backbone.data_models.user import UserDataModel
from fastapi import APIRouter
from pydantic import EmailStr
from backbone.bases.base_request import BaseRequest, BaseResponse
from backbone.exceptions import Exception400AlreadyExist
from bootstrap.setup_locator import loc

router = APIRouter(prefix="/user", tags=["user"])


class UserRequest(
    BaseRequest,
    PydanticMixinPhoneRequired,
    PydanticMixinEmailRequired,
    PydanticMixinUsernameRequired,
    PydanticMixinPasswordOptional,
):
    pass


class UserResponse(
    BaseResponse,
    PydanticMixinContact,
    PydanticMixinUsernameRequired,
    PydanticMixinUserID,
):
    pass


@router.post("", response_model=UserResponse)
async def create_user(request: UserRequest):
    tortoiseAdapter: TortoiseAdapter = loc.get("TortoiseAdapter")
    authAdapter: AuthAdapter = loc.get("AuthAdapter")
    existing_user = await UserDataModel.get_or_none(username=request.username)
    if existing_user:
        raise Exception400AlreadyExist()
    async with tortoiseAdapter.transaction():
        user: UserDataModel = await UserDataModel.create(
            username=request.username,
            password=request.password,
            phone=request.phone,
            email=request.email,
        )
        devlog(user.id)
        devlog("user.id==========================")
        await authAdapter.create_user(
            UserAuthAdapterDTO(
                user_id=user.id,
                username=request.username,
                password=request.password,
                phone=request.phone,
                email=request.email,
            )
        )
    return UserResponse(
        user_id=user.id,
        username=request.username,
        phone=request.phone,
        email=request.email,
    )
