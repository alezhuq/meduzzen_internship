from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.schemas.user_schemas import UserSignInSchema, UserSchema
from app.db.services.userservice import UserService, TokenService
from app.api.dependencies.dependencies import get_repository
from app.core.token import VerifyToken
from fastapi.security import HTTPBearer
from app.core.security import compare_hash
from app.schemas.token_schemas import Token
from app.core.exceptions import NotFoundException

router = APIRouter()

TOKEN_AUTH_SCHEME = HTTPBearer()


@router.post("/user/auth", response_model=Token)
async def authenticate(
        login: UserSignInSchema,
        user_service: UserService = Depends(get_repository(UserService))
) -> Token:
    """default authentication"""
    try:
        user = await user_service.get_by_email(user_email=login.email)
    except NotFoundException as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    user_data = user.dict()
    user_email = user_data.get("email")
    user_id = user_data.get("id")
    if user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="user is none")
    elif not compare_hash(login.password.encode(), user.password.encode()):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="password issue")
    return Token(
        token=VerifyToken.create_custom(user_id=user_id, data={"email": user_email})
    )


@router.get("/api/private", response_model=Token)
async def private(
        token: str = Depends(TOKEN_AUTH_SCHEME),
        user_service: UserService = Depends(get_repository(UserService))
) -> Token:
    """auth0 authentication/registration"""
    user = await TokenService.create_from_auth0(token, user_service)
    return Token(
        token=VerifyToken.create_custom(user_id=user.id, data={"email": user.email})
    )


