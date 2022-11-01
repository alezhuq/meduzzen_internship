import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import BaseModel


class Companies(BaseModel):
    __tablename__ = "Company"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sa.Column(sa.String, primary_key=True, unique=True)
    description = sa.Column(sa.String)
    hidden = sa.Column(sa.Boolean, default=False)
    users = relationship("UsersInCompanies", back_populates="companies")
    invites = relationship("Invites", back_populates="companies")


class UsersInCompanies(BaseModel):
    __tablename__ = "UserInCompany"
    user_id = sa.Column(sa.ForeignKey("User.id", ondelete="CASCADE"), primary_key=True)
    company_id = sa.Column(sa.ForeignKey("Company.id", ondelete="CASCADE"), primary_key=True)
    is_owner = sa.Column(sa.Boolean, default=False)
    is_staff = sa.Column(sa.Boolean, default=False)
    users = relationship("Users", back_populates="companies")
    companies = relationship("Companies", back_populates="users", cascade="save-update")


class Invites(BaseModel):
    __tablename__ = "Invite"
    user_id = sa.Column(sa.ForeignKey("User.id", ondelete="CASCADE"), primary_key=True)
    company_id = sa.Column(sa.ForeignKey("Company.id", ondelete="CASCADE"), primary_key=True)
    # pending status can contain one of these values : accepted, declined, requested, pending (default - pending)
    pending_status = sa.Column(sa.String, default="pending")
    users = relationship("Users", back_populates="invites", cascade="all, delete")
    companies = relationship("Companies", back_populates="invites", cascade="all, delete")
