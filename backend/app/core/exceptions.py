from typing import Any

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class NotFoundException(HTTPException):
    def __init__(self, detail: Any = "not found") -> None:
        status_code = 404
        detail = detail
        super().__init__(status_code=status_code, detail=detail)


class AlreadyExistsException(HTTPException):
    def __init__(self, detail: Any = "already exists") -> None:
        status_code = 400
        detail = detail
        super().__init__(status_code=status_code, detail=detail)

