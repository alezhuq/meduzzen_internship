from .core import CoreSchema, IdMixin
from .user_schemas import UserSchema


class CompanySchema(IdMixin, CoreSchema):
    name: str
    description: str
    hidden: bool


class CompanyResponseSchema(CoreSchema):
    name: str
    description: str


class CompanyCreatechema(CoreSchema):
    name: str
    description: str
    hidden: bool


class UserInCompanySchema(CoreSchema):
    user = UserSchema
    company = CompanySchema


class InviteSchema(CoreSchema):
    user = UserSchema
    company = CompanySchema
