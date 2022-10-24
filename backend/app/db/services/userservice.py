from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.db.services.base import BaseService
from app.db.models.user import Users
from app.core.security import hash_string
from app.core.exceptions import UserNotFoundException, UserAlreadyexistsException
from app.schemas.user_schemas import (
    UserSchema,
    RegisterSchema,
    UserUpdatePasswordSchema,
    UserSingleResponseSchema
)


class UserService(BaseService):

    async def create_user(self, *, new_user: RegisterSchema) -> UserSingleResponseSchema:
        raw_values = new_user.dict()
        query_values = {
            "username": raw_values.get("username"),
            "email": raw_values.get("email"),
            "password": hash_string(str.encode(raw_values.get("password1"))).decode(),
        }

        try:
            query = Users.insert()
            user_id = await self.db.execute(query=query, values=query_values)
        except UniqueViolationError:
            raise UserAlreadyexistsException("user already exists")

        query_values.pop("password")
        user = UserSingleResponseSchema(**query_values)

        return user

    async def get_all_users(self, limit: int = 200, offset: int = 0) -> list[UserSingleResponseSchema]:
        query = Users.select().limit(limit).offset(offset)
        users = await self.db.fetch_all(query=query)
        return [UserSingleResponseSchema(**user) for user in users]

    async def get_by_id(self, user_id: int) -> UserSchema:
        query = Users.select().where(Users.c.id == user_id)
        user = await self.db.fetch_one(query=query)
        if user is None:
            raise UserNotFoundException("user was not found")
        return UserSchema(**user)

    async def get_by_email(self, user_email: str) -> UserSchema:
        query = Users.select().where(Users.c.email == user_email)
        user = await self.db.fetch_one(query=query)
        if user is None:
            raise UserNotFoundException("user was not found")
        return UserSchema(**user)

    async def update_user_password(self, user_id: int, user: UserUpdatePasswordSchema) -> dict:
        query_values = {"password": hash_string(str.encode(user.new_password)).decode()}
        query = Users.update().where(Users.c.id == user_id).values(query_values)
        try:
            await self.db.fetch_one(query=query)
        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error updating the password")
        return {"status": "changed"}

    async def delete_user_by_id(self, user_id: int):
        query = Users.delete().where(Users.c.id == user_id)
        result = await self.db.execute(query=query)
        return result
