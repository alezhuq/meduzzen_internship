from databases import Database


class BaseService(object):
    def __init__(self, db: Database) -> None:
        self.db = db
