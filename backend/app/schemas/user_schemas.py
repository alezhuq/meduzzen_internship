from pydantic import validator, EmailStr
from email_validator import validate_email, EmailNotValidError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .core import CoreSchema, IdMixin
from fastapi.exceptions import HTTPException


class UserSchema(IdMixin, CoreSchema):
    username: str
    password: str
    email: EmailStr

    def __str__(self):
        return self.username


class RegisterSchema(CoreSchema):
    username: str
    email: EmailStr
    password1: str
    password2: str

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')

    @validator('email')
    def validate_user_email(cls, v):
        try:
            validate_email(v, check_deliverability=True)

        except EmailNotValidError as e:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY)

        return v


class UserSignInSchema(CoreSchema):
    email: str
    password: str


class UserUpdatePasswordSchema(CoreSchema):
    old_password: str
    new_password: str
    new_confirm: str

    @validator("new_password")
    def old_new_passwords_match(cls, v, values, **kwargs):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('passwords match')
        return v

    @validator("new_confirm")
    def new_confirm_passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v


class UserSingleResponseSchema(CoreSchema):
    username: str
    email: EmailStr


class TokenSchema(CoreSchema):
    access_token: str
    token_type: str


class SuccessfulResult(CoreSchema):
    status: str
