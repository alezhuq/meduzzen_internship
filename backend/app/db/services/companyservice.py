from asyncpg import UniqueViolationError
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from app.db.models.base import session
from app.core.exceptions import AlreadyExistsException, NotFoundException
from .base import BaseService
from app.db.models.company import Companies, UsersInCompanies, Invites
from app.db.models.user import Users
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema
from app.schemas.user_schemas import UserSchema, SuccessfulResult
from strenum import StrEnum

Company = Companies.__table__
UserInCompany = UsersInCompanies.__table__


class InviteStatus(StrEnum):
    accepted = "accepted",
    declined = "declined",
    requested = "requested",
    pending = "pending"


class CompanyService(BaseService):
    async def create_company(self, *, user: UserSchema, new_company: CompanyCreatechema) -> SuccessfulResult:
        try:
            curr_user = session.query(Users).filter_by(id=user.id).first()
            userincomp = UsersInCompanies(user_id=curr_user.id, is_owner=True)
            company = Companies(name=new_company.name, description=new_company.description, hidden=new_company.hidden)
            userincomp.companies = company
            session.add_all([company, userincomp])
            curr_user.companies.append(userincomp)
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create company")
        return SuccessfulResult(status="created")

    async def check_owner(self, company_id: int, user_id) -> bool:
        is_owner = session.query(UsersInCompanies).filter_by(company_id=company_id, user_id=user_id).first()
        return False if not is_owner else is_owner.is_owner

    async def get_by_id(self, company_id: int) -> CompanySchema:
        query = Company.select().where(Company.c.id == company_id)
        result = await self.db.fetch_one(query=query)
        if result is None:
            raise NotFoundException("company was not found")
        return CompanySchema(**result)

    async def change_hidden(self, *, company_id: int, new_status: bool) -> SuccessfulResult:
        query_values = {
            "hidden": new_status
        }
        query = Company.update().where(
            Company.c.id == company_id
        ).values(query_values)
        try:
            await self.db.fetch_one(query=query)
        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error updating the status")

        return SuccessfulResult(status="changed")

    async def change_name_description(self, *, company_id: int, company: CompanyResponseSchema) -> SuccessfulResult:
        query_values = company.dict()
        query = Company.update().where(Company.c.id == company_id).values(query_values)
        try:
            await self.db.fetch_one(query=query)
        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error updating the status")

        return SuccessfulResult(status="changed")

    async def delete_company(self, *, company_id: int) -> SuccessfulResult:
        query = Company.delete().where(Company.c.id == company_id)
        try:
            await self.db.execute(query=query)
        except Exception:
            HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="error when deleting the company")
        return SuccessfulResult(status="deleted")

    async def invite_to_company(self, *, company_id: int, user_id: int) -> SuccessfulResult:
        try:
            invited_user = session.query(Users).filter_by(id=user_id).first()
            curr_company = session.query(Companies).filter_by(id=company_id).first()

            invite = Invites(user_id=invited_user.id, company_id=curr_company.id, pending_status="pending")
            invite.companies = curr_company
            invited_user.invites.append(invite)
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create invite")
        return SuccessfulResult(status="created")

    async def kick_from_company(self, *, company_id: int, user_id: int) -> SuccessfulResult:
        try:
            session.query(UsersInCompanies).filter_by(user_id=user_id, company_id=company_id).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create invite")
        return SuccessfulResult(status="created")

    async def request_invite(self, *, company_id: int, user_id: int) -> SuccessfulResult:
        try:
            curr_user = session.query(Users).filter_by(id=user_id).first()
            curr_company = session.query(Companies).filter_by(id=company_id).first()

            invite = Invites(user_id=curr_user.id, company_id=curr_company.id, pending_status="requested")
            invite.companies = curr_company
            curr_user.invites.append(invite)
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status="created")

    async def reply_to_invite_request(self, *, user_id: int, company_id: int, reply: InviteStatus) -> SuccessfulResult:
        try:
            session.query(Invites).filter_by(
                user_id=user_id,
                company_id=company_id
            ).update({"pending_status": reply})
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status=reply)

    async def accept_decline_invite(self, *, user_id: int, company_id: int, accept: bool) -> SuccessfulResult:
        try:
            invite = session.query(Invites).filter_by(user_id=user_id, company_id=company_id).first()
            reply = "accepted" if accept else "declined"
            invite.update({"pending_status": reply})
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status=reply)

    async def change_staff_status(self, *, user_id: int, company_id: int, new_status: bool) -> SuccessfulResult:
        try:
            session.query(UsersInCompanies).filter_by(
                user_id=user_id,
                company_id=company_id
            ).update({"is_staff": new_status})
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status="changed")

    async def get_all_companies(self, limit: int = 200, offset: int = 0):
        query = Company.select().where(Company.c.hidden == False).limit(limit).offset(offset)
        companies = await self.db.fetch_all(query=query)
        return [CompanyResponseSchema(**company) for company in companies]
