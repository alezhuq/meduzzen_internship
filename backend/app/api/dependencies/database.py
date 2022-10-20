from typing import Callable, Type
from databases import Database
from fastapi import Depends
from starlette.requests import Request
from app.db.services.base import BaseService


def get_database(request: Request) -> Database:
    return request.app.state._db


def get_repository(Repo_type: Type[BaseService]) -> Callable:
    def get_repo(db: Database = Depends(get_database)) -> BaseService:
        return Repo_type(db)
    return get_repo


