from databases import Database
from strenum import StrEnum


class BaseService(object):
    def __init__(self, db: Database) -> None:
        self.db = db


class InviteStatus(StrEnum):
    accepted = "accepted",
    declined = "declined",
    requested = "requested",
    pending = "pending"

