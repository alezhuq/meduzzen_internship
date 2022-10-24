from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from fastapi_pagination import Page, paginate, Params

from app.schemas.user_schemas import RegisterSchema, UserSingleResponseSchema, UserUpdatePasswordSchema, UserSchema
from app.db.services.userservice import UserService
from app.api.dependencies.dependencies import get_repository, get_current_user
from app.core.security import compare_hash

router = APIRouter()
DEFAULT_PAGINATION_PAGE = 1
DEFAULT_PAGINATION_SIZE = 10


@router.get("/")
def read_root():
    return {"status": "Working"}


@router.post("/", response_model=UserSingleResponseSchema, name="user:create-user", status_code=HTTP_201_CREATED)
async def create_new_user(
        new_user: RegisterSchema,
        user_service: UserService = Depends(get_repository(UserService))) -> UserSingleResponseSchema:
    created_user = await user_service.create_user(new_user=new_user)
    if created_user is None:
        raise HTTPException(status_code=422, detail="can't create user")
    return created_user


@router.get("/user/all", response_model=Page[UserSingleResponseSchema])
async def get_users(
        pagination_page: str = DEFAULT_PAGINATION_PAGE,
        pagination_size: int = DEFAULT_PAGINATION_SIZE,
        user_service: UserService = Depends(get_repository(UserService))):
    page = int(pagination_page)
    users = await user_service.get_all_users()
    if users is None:
        return {}
    return paginate(users, Params(page=page, size=pagination_size))


@router.get("/user/id/{user_id}")
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_repository(UserService))):
    try:
        user = await user_service.get_by_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return user


@router.put("/user/id/{user_id}/edit_password")
async def change_user_password(
        user_id: int,
        user: UserUpdatePasswordSchema,
        user_service: UserService = Depends(get_repository(UserService)),
        current_user: UserSchema = Depends(get_current_user)):
    try:
        requested_user = await user_service.get_by_id(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    if not requested_user.email == current_user.email:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="you are not authorized as that user")
    if not compare_hash(user.old_password.encode(), requested_user.password.encode()):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="passwords do not match")
    user = await user_service.update_user_password(user_id, user)
    return user


@router.delete("/user/id/{user_id}/delete")
async def delete_user(
        user_id: int,
        user_service: UserService = Depends(get_repository(UserService)),
        current_user: UserSchema = Depends(get_current_user)
):
    try:
        requested_user = await user_service.get_by_id(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    if not requested_user.email == current_user.email:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="you are not authorized as that user")
    try:
        await user_service.delete_user_by_id(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    return {"status": "deleted"}
