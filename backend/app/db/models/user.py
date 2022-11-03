import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    email = sa.Column(sa.String, unique=True)
    username = sa.Column(sa.String)
    password = sa.Column(sa.String)
    register_date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    is_active = sa.Column(sa.Boolean)
    companies = relationship("Member", back_populates="users")
    invites = relationship("Invite", back_populates="users")

