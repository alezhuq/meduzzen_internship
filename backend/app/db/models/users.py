from sqlalchemy.orm import declarative_base

import sqlalchemy as sa
import datetime

Base = declarative_base()

class Users(Base):
    __tablename__ = 'Users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    email = sa.Column(sa.String, primary_key=True, unique=True)
    username = sa.Column(sa.String)
    password = sa.Column(sa.String, primary_key=True)
    register_date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    is_active = sa.Column(sa.Boolean)



