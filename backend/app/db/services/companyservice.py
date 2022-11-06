from asyncpg import UniqueViolationError
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from app.db.models.base import session
from app.core.exceptions import AlreadyExistsException, NotFoundException
from .base import BaseService
from app.db.models.company import Company, Member, Invite
from app.db.models.user import User
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema, MemberSchema
from app.schemas.user_schemas import UserSchema
from app.schemas.core import SuccessfulResult
from .base import InviteStatus

Companies = Company.__table__
UsersInCompanies = Member.__table__


def check_owner(func):
    async def wrapper(*args, **kwargs):
        try:
            user = session.query(Member).filter_by(
                company_id=kwargs.get("company_id", 0),
                user_id=kwargs.get("owner_id", 0)
            ).first()

        except Exception:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="invalid user or company")
        if user and user.is_owner:
            return await func(*args, **kwargs)
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="you don't have permissions to do this")

    return wrapper


def check_staff(func):
    async def wrapper(*args, **kwargs):
        try:
            user = session.query(Member).filter_by(
                company_id=kwargs.get("company_id", 0),
                user_id=kwargs.get("staff_id", 0)
            ).first()

        except Exception:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="invalid user or company")
        if user and (user.is_owner or user.is_staff):
            return await func(*args, **kwargs)
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="you don't have permissions to do this")

    return wrapper


class CompanyService(BaseService):

    async def create_company(self, *, user: UserSchema, new_company: CompanyCreatechema) -> SuccessfulResult:
        try:
            curr_user = session.query(User).filter_by(id=user.id).first()

            company = Company(name=new_company.name, description=new_company.description, hidden=new_company.hidden)
            session.add(company)
            session.commit()
            created_company = session.query(Company).filter_by(name=company.name).first()
            member = Member(user_id=curr_user.id, company_id=created_company.id, is_owner=True)
            session.add(member)
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
        return SuccessfulResult(status="created")

    async def get_by_id(self, company_id: int) -> CompanySchema:
        query = Companies.select().where(Companies.c.id == company_id)
        result = await self.db.fetch_one(query=query)
        if result is None:
            raise NotFoundException("company was not found")
        return CompanySchema(**result)

    @check_owner
    async def change_visibility(self, *, owner_id: int, company_id: int, new_status: bool) -> SuccessfulResult:
        query_values = {
            "hidden": new_status
        }
        query = Companies.update().where(
            Companies.c.id == company_id
        ).values(query_values)
        try:
            await self.db.fetch_one(query=query)
        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error updating the status")

        return SuccessfulResult(status="changed")

    @check_owner
    async def change_name_description(self, *, owner_id: int, company_id: int,
                                      company: CompanyResponseSchema) -> SuccessfulResult:
        query_values = company.dict()
        query = Companies.update().where(Companies.c.id == company_id).values(query_values)
        try:
            await self.db.fetch_one(query=query)
        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error updating the status")

        return SuccessfulResult(status="changed")

    @check_owner
    async def delete_company(self, *, owner_id: int, company_id: int) -> SuccessfulResult:
        query = Companies.delete().where(Companies.c.id == company_id)
        try:
            await self.db.execute(query=query)
        except Exception:
            HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error when deleting the company")
        return SuccessfulResult(status="deleted")

    @check_owner
    async def invite_to_company(self, *, company_id: int, user_id: int, owner_id: int) -> SuccessfulResult:
        try:
            invited_user = session.query(User).filter_by(id=user_id).first()
            curr_company = session.query(Company).filter_by(id=company_id).first()

            invite = Invite(user_id=invited_user.id, company_id=curr_company.id,
                            pending_status=InviteStatus.pending)
            session.add(invite)
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create invite")
        return SuccessfulResult(status="created")

    @check_owner
    async def kick_from_company(self, *, company_id: int, owner_id: int, member_id: int) -> SuccessfulResult:
        try:
            session.query(Member).filter_by(user_id=member_id, company_id=company_id).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create invite")
        return SuccessfulResult(status="created")

    async def request_invite(self, *, company_id: int, user_id: int) -> SuccessfulResult:
        try:
            curr_user = session.query(User).filter_by(id=user_id).first()
            curr_company = session.query(Company).filter_by(id=company_id).first()

            invite = Invite(user_id=curr_user.id, company_id=curr_company.id, pending_status=InviteStatus.requested)
            session.add(invite)
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status="created")

    @check_owner
    async def reply_to_invite_request(self, *, user_id: int, owner_id: int, company_id: int,
                                      reply: InviteStatus) -> SuccessfulResult:
        try:
            invite = session.query(Invite).filter_by(
                user_id=user_id,
                company_id=company_id
            ).first()

            if invite.pending_status == InviteStatus.requested:
                session.query(Invite).filter_by(
                    user_id=user_id,
                    company_id=company_id
                ).update({"pending_status": reply})
                session.commit()
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="can respond only to requested invites")
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't reply to invite")
        return SuccessfulResult(status=reply)

    async def accept_decline_invite(self, *, user_id: int, company_id: int, accept: bool) -> SuccessfulResult:
        try:
            invite = session.query(Invite).filter_by(user_id=user_id, company_id=company_id).first()
            if invite.pending_status == InviteStatus.pending:
                reply = InviteStatus.accepted if accept else InviteStatus.declined
                session.query(Invite).filter_by(user_id=user_id, company_id=company_id).update(
                    {"pending_status": reply})
                session.commit()
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="can respond only to pending invites")
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't reply to invite")
        return SuccessfulResult(status=reply)

    @check_owner
    async def change_staff_status(self, *, owner_id: int, changed_user_id: int, company_id: int,
                                  new_status: bool) -> SuccessfulResult:
        try:
            session.query(Member).filter_by(
                user_id=changed_user_id,
                company_id=company_id
            ).update({"is_staff": new_status})
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status="changed")

    async def get_all_companies(self, limit: int = 200, offset: int = 0) -> list[CompanyResponseSchema]:
        query = Companies.select().where(Companies.c.hidden == False).limit(limit).offset(offset)
        companies = await self.db.fetch_all(query=query)
        return [CompanyResponseSchema(**company) for company in companies]
