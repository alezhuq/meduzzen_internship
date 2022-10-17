from pydantic import BaseModel


class CoreSchema(BaseModel):
    # common logic shared by all schemas goes here
    pass


class UserMixin(BaseModel):
    id: int
