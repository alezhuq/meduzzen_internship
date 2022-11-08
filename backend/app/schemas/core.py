from pydantic import BaseModel


class CoreSchema(BaseModel):
    # common logic shared by all schemas goes here
    pass


class IdMixin(BaseModel):
    id: int


class SuccessfulResult(CoreSchema):
    status: str