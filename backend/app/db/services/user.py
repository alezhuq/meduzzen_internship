import sqlalchemy as sa
import datetime
from app.db.services.base import BaseService
from asyncpg.exceptions import UniqueViolationError
from app.db.models.user import Users
from app.core.security import hash_string, compare_hash
from app.core.exceptions import UserNotFoundException, UserAlreadyexistsException
from app.schemas.schemas import (
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

    async def get_by_id(self, user_id: int) -> UserSingleResponseSchema:
        query = Users.select().where(Users.c.id == user_id)
        user = await self.db.fetch_one(query=query)
        if user is None:
            raise UserNotFoundException("user was not found")
        return UserSingleResponseSchema(**user)

    async def update_user_password(self, user_id: int, user: UserUpdatePasswordSchema) -> UserSingleResponseSchema:
        query_values = {"password": hash_string(str.encode(user.new_password)).decode()}
        query = Users.update().where(Users.c.id == user_id).values(query_values)
        changed = await self.db.fetch_one(query=query)
        return UserSingleResponseSchema(**changed)

    async def delete_user_by_id(self, user_id: int):
        query = Users.delete().where(Users.c.id == user_id)
        result = await self.db.execute(query=query)
        return result
