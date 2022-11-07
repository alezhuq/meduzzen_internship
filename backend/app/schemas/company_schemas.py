from .core import CoreSchema, IdMixin


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


class MemberSchema(CoreSchema):
    user_id: int
    company_id: int
    is_owner: bool
    is_staff: bool

