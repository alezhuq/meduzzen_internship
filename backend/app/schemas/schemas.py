from pydantic import BaseModel, ValidationError, validator, EmailStr
from email_validator import validate_email, EmailNotValidError
from .core import CoreSchema, UserMixin


class UserSchema(UserMixin, CoreSchema):
    username: str
    password: str

    email: EmailStr


class SignInSchema(CoreSchema):
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
            raise ValidationError("can't validate email")


class SignUpSchema(CoreSchema):
    username: str
    password: str


class UserUpdatePasswordSchema(CoreSchema):
    old_password: str
    new_password: str
    new_confirm: str

    @validator("new_password")
    def old_new_passwords_match(cls, v, values, **kwargs):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('passwords match')

    @validator("new_confirm")
    def new_confirm_passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')



"""to get list of users :
[UserSingleResponseSchema(user) for user in users]
"""
class UserSingleResponseSchema(CoreSchema):
    username: str
    email: EmailStr

