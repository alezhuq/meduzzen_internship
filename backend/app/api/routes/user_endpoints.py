from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED

from app.schemas.schemas import RegisterSchema, UserSchema, UserSingleResponseSchema, UserUpdatePasswordSchema
from app.db.services.user import UserService
from app.api.dependencies.database import get_repository
from fastapi_pagination import Page, paginate, Params

router = APIRouter()
DEFAULT_PAGINATION_PAGE = 1
DEFAULT_PAGINATION_SIZE = 10


@router.get("/")
def read_root():
    return {"status": "Working"}


@router.post("/", response_model=UserSchema, name="user:create-user", status_code=HTTP_201_CREATED)
async def create_new_user(
        new_user: RegisterSchema,
        user_service: UserService = Depends(get_repository(UserService))) -> UserSchema:
    created_user = await user_service.create_user(new_user=new_user)
    if created_user is None:
        raise HTTPException(status_code=422, detail="can't create user")
    return created_user


@router.get("/user/all", response_model=Page[UserSingleResponseSchema])
async def get_users(
        user_service: UserService = Depends(get_repository(UserService)),
        pagination_page: int = DEFAULT_PAGINATION_PAGE,
        pagination_size: int = DEFAULT_PAGINATION_SIZE):
    users = await user_service.get_all_users()
    if users is None:
        raise HTTPException(status_code=404, detail="user was not found")
    return paginate(users, Params(page=pagination_page, size=pagination_size))


@router.get("/user/{user_id}")
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_repository(UserService))):
    try:
        user = await user_service.get_by_id(user_id)
    except Exception:
        raise HTTPException(status_code=404, detail="user was not found")
    return user


@router.put("/user/{user_id}/edit_password")
async def change_user_password(
        user_id: int,
        user: UserUpdatePasswordSchema,
        user_service: UserService = Depends(get_repository(UserService))):

    user = await user_service.update_user_password(user_id, user)
    return user


@router.delete("/user/{user_id}/delete")
async def delete_user(
        user_id: int,
        user_service: UserService = Depends(get_repository(UserService))) -> None:
    await user_service.delete_user_by_id(user_id=user_id)
