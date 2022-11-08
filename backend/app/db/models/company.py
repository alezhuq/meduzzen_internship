import sqlalchemy as sa
from sqlalchemy.orm import relationship
from ..services.base import InviteStatus

from .base import BaseModel
from .quiz import Quiz # without this import company table doesn't work

class Company(BaseModel):
    __tablename__ = "company"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sa.Column(sa.String, unique=True)
    description = sa.Column(sa.String)
    hidden = sa.Column(sa.Boolean, default=False)
    users = relationship("Member", back_populates="companies")
    invites = relationship("Invite", back_populates="companies")
    quizzes = relationship("Quiz", back_populates="company")


class Member(BaseModel):
    __tablename__ = "member"
    user_id = sa.Column(sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    company_id = sa.Column(sa.ForeignKey("company.id", ondelete="CASCADE"))
    is_owner = sa.Column(sa.Boolean, default=False)
    is_staff = sa.Column(sa.Boolean, default=False)
    users = relationship("User", back_populates="companies")
    companies = relationship("Company", back_populates="users", cascade="save-update")


class Invite(BaseModel):
    __tablename__ = "invite"
    user_id = sa.Column(sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    company_id = sa.Column(sa.ForeignKey("company.id", ondelete="CASCADE"))
    # pending status can contain one of these values : accepted, declined, requested, pending (default - pending)
    status = sa.Column(sa.Enum(InviteStatus), default=str(InviteStatus.pending))
    users = relationship("User", back_populates="invites", cascade="all, delete")
    companies = relationship("Company", back_populates="invites", cascade="all, delete")
