import time

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.dependencies.dependencies import get_repository
from app.core.exceptions import UserNotFoundException
from app.core.token import VerifyToken
from app.db.services.userservice import UserService
from app.schemas.user_schemas import RegisterSchema


class TokenService(object):
    @staticmethod
    async def create_from_auth0(token: str = Depends(HTTPBearer()),
                          user_service: UserService = Depends(get_repository(UserService))):
        result = VerifyToken(token.credentials).verify()
        if result.get('status'):
            return HTTPException(status_code=HTTP_400_BAD_REQUEST)
        user_email = result.get("https://HRassessment-project.com/email")
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
