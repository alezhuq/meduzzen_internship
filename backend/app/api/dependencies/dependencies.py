from typing import Callable, Type
from databases import Database
from fastapi import Depends
from fastapi.security import HTTPBearer
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.db.services.base import BaseService
from app.db.services.userservice import UserService
from app.schemas.user_schemas import UserSchema
from app.core.token import VerifyToken


def get_database(request: Request) -> Database:
    return request.app.state._db


def get_repository(Repo_type: Type[BaseService]) -> Callable:
    def get_repo(db: Database = Depends(get_database)) -> BaseService:
        return Repo_type(db)

    return get_repo


async def get_current_user(
        user_service: UserService = Depends(get_repository(UserService)),
        token: str = Depends(HTTPBearer()),
) -> UserSchema:
    cred_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credentials are not valid")
    try:
        payload = VerifyToken.verify_custom(token.credentials)
        email: str = payload.get("email")
    except Exception:
        payload = VerifyToken(token.credentials).verify()
        if payload.get('status'):
            raise cred_exception
        email = payload.get("https://HRassessment-project.com/email")

    if email is None:
        raise cred_exception
    user = await user_service.get_by_email(user_email=email)
    if user is None:
        raise cred_exception
    return user
