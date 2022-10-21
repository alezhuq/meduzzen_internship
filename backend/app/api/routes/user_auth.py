import time

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.schemas.schemas import UserSchema, UserSignInSchema, RegisterSchema
from app.db.services.user import UserService
from app.api.dependencies.database import get_repository
from app.core.token import VerifyToken
from fastapi.security import HTTPBearer
from asyncpg.exceptions import InvalidPasswordError
from app.core.security import compare_hash
from app.core.exceptions import UserNotFoundException

router = APIRouter()

TOKEN_AUTH_SCHEME = HTTPBearer()


@router.post("/user/auth", response_model=UserSchema)
async def authenticate(
        login: UserSignInSchema,
        user_service: UserService = Depends(get_repository(UserService))) -> UserSchema:
    """default authentication"""
    user = await user_service.get_by_email(user_email=login.email)
    if user is None or not compare_hash(login.password.encode(), user.password.encode()):
        raise InvalidPasswordError
    return user


@router.get("/api/private")
async def private(token: str = Depends(TOKEN_AUTH_SCHEME),
            user_service: UserService = Depends(get_repository(UserService))):
    """auth0 authentication/registration"""
    result = VerifyToken(token.credentials).verify()
    if result.get('status'):
        return HTTPException(status_code=HTTP_400_BAD_REQUEST)
    user_email = result.get("https://example.com/email")
    try:
        user = await user_service.get_by_email(user_email=user_email)
    except UserNotFoundException:
        password = str(time.time()).encode()
        new_user = RegisterSchema(
            username=user_email,
            email=user_email,
            password1=password,
            password2=password,
        )
        user = await user_service.create_user(new_user=new_user)

    return user
