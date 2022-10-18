from app.db.services.base import BaseService
from app.schemas.schemas import (
    UserSchema,
    RegisterSchema,
    SignInSchema,
    UserUpdatePasswordSchema,
    UserSingleResponseSchema
)

CREATE_USER_QUERY = """
    INSERT INTO "Users" (username, email, password)
    VALUES (:username, :email, :password1)
    RETURNING id, username, email, password;
"""

SELECT_ALL_USERS = """
    SELECT username, email FROM "Users";
"""

SELECT_USER_BY_ID = """
    SELECT username, email FROM "Users"
    WHERE id=:id
"""

CHANGE_USER_PASSWORD = """
    UPDATE "Users"
    SET password =:new_password
    WHERE id=:id
    RETURNING username, email;
"""

DELETE_USER_BY_ID = """
    DELETE FROM "Users"
    WHERE id = :user_id;
"""


class UserService(BaseService):
    async def create_user(self, *, new_user: RegisterSchema) -> UserSchema:
        query_values = new_user.dict()
        query_values.pop("password2")
        user = await self.db.fetch_one(query=CREATE_USER_QUERY, values=query_values)
        return UserSchema(**user)

    async def get_all_users(self) -> list:
        users = await self.db.fetch_all(query=SELECT_ALL_USERS)
        return [UserSingleResponseSchema(**user) for user in users]

    async def get_by_id(self, user_id: int) -> UserSingleResponseSchema:
        user = await self.db.fetch_one(query=SELECT_USER_BY_ID, values={"id": user_id})
        return UserSingleResponseSchema(**user)

    async def update_user_password(self, user_id: int, user: UserUpdatePasswordSchema) -> UserSingleResponseSchema:
        query_values = {"id": user_id, "new_password": user.new_password}
        changed = await self.db.fetch_one(query=CHANGE_USER_PASSWORD, values=query_values)
        return UserSingleResponseSchema(**changed)

    async def delete_user_by_id(self, user_id: int) -> None:
        query_values = {"user_id": user_id}
        await self.db.fetch_one(query=DELETE_USER_BY_ID, values=query_values)
