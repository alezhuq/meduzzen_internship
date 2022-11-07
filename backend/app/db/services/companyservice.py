from fastapi import HTTPException, Depends
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.api.dependencies.dependencies import get_session
from app.core.exceptions import NotFoundException
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
            session = kwargs.get("session", Depends(get_session))
            user_request = await session.execute(select(Member).where(
                Member.company_id == kwargs.get("company_id", 0),
                Member.user_id == kwargs.get("owner_id", 0)
            ))
            user = user_request.scalars().first()
        except Exception:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="invalid user or company")
        if user.is_owner:
            return await func(*args, **kwargs)
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="you don't have permissions to do this")

    return wrapper


def check_staff(func):
    async def wrapper(*args, **kwargs):
        try:
            session = kwargs.get("session", None)
            user_request = await session.execute(select(Member).where(
                Member.company_id == kwargs.get("company_id", 0),
                Member.user_id == kwargs.get("staff_id", 0)
            ))
            user = user_request.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="invalid user or company")
        if user.is_owner or user.is_staff:
            return await func(*args, **kwargs)
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="you don't have permissions to do this")

    return wrapper


class CompanyService(BaseService):
    @staticmethod
    async def create_company(*, session: AsyncSession, user: UserSchema,
                             new_company: CompanyCreatechema) -> SuccessfulResult:
        try:
            user_request = await session.execute(select(User).where(User.id == user.id))
            curr_user = user_request.scalars().first()
            company = Company(name=new_company.name, description=new_company.description, hidden=new_company.hidden)
            session.add(company)
            await session.commit()
            company_request = await session.execute(select(Company).where(Company.name == company.name))
            created_company = company_request.scalars().first()
            member = Member(user_id=curr_user.id, company_id=created_company.id, is_owner=True)
            session.add(member)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"can't create company, {str(e)}")
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

    @staticmethod
    @check_owner
    async def invite_to_company(*, session: AsyncSession, company_id: int, user_id: int,
                                owner_id: int) -> SuccessfulResult:
        try:
            invited_user_request = await session.execute(select(User).where(User.id == user_id))
            curr_company_request = await session.execute(select(Company).where(Company.id == company_id))
            invited_user = invited_user_request.scalars().first()
            curr_company = curr_company_request.scalars().first()
            invite = Invite(user_id=invited_user.id, company_id=curr_company.id,
                            pending_status=InviteStatus.pending)
            session.add(invite)
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create invite")
        return SuccessfulResult(status="created")

    @staticmethod
    @check_owner
    async def kick_from_company(*, session: AsyncSession, company_id: int, owner_id: int,
                                member_id: int) -> SuccessfulResult:
        try:
            await session.execute(delete(Member).where(Member.user_id == member_id, Member.company_id == company_id))
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't create invite")
        return SuccessfulResult(status="created")

    @staticmethod
    async def request_invite(*, session: AsyncSession, company_id: int, user_id: int) -> SuccessfulResult:
        try:
            curr_user_request = await session.execute(select(User).where(User.id == user_id))
            curr_company_request = await session.execute(select(Company).where(Company.id == company_id))
            curr_user = curr_user_request.scalars().first()
            curr_company = curr_company_request.scalars().first()

            invite = Invite(user_id=curr_user.id, company_id=curr_company.id,
                            pending_status=InviteStatus.requested)
            session.add(invite)
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status="created")

    @staticmethod
    @check_owner
    async def reply_to_invite_request(*, session: AsyncSession, user_id: int, owner_id: int, company_id: int,
                                      reply: InviteStatus) -> SuccessfulResult:
        try:
            invite_request = await session.execute(select(Invite).where(
                Invite.user_id == user_id,
                Invite.company_id == company_id
            ))
            invite = invite_request.scalars().first()
            if invite.pending_status == InviteStatus.requested:
                await session.execute(update(Invite).where(
                    Invite.user_id == user_id,
                    Invite.company_id == company_id
                ).values({"pending_status": reply}))
                await session.commit()
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="can respond only to requested invites")
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't reply to invite")
        return SuccessfulResult(status=reply)

    @staticmethod
    async def accept_decline_invite(*, session: AsyncSession, user_id: int, company_id: int,
                                    accept: bool) -> SuccessfulResult:
        try:
            invite_request = await session.execute(select(Invite).where(
                Invite.user_id == user_id, Invite.company_id == company_id
            ))
            invite = invite_request.scalars().first()
            if invite.pending_status == InviteStatus.pending:
                reply = InviteStatus.accepted if accept else InviteStatus.declined
                await session.execute(update(Invite).where(
                    Invite.user_id == user_id,
                    Invite.company_id == company_id
                ).values({"pending_status": reply}))
                await session.commit()
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="can respond only to pending invites")
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't reply to invite")
        return SuccessfulResult(status=reply)

    @staticmethod
    @check_owner
    async def change_staff_status(*, session: AsyncSession, owner_id: int, changed_user_id: int, company_id: int,
                                  new_status: bool) -> SuccessfulResult:
        try:
            await session.execute(update(Member).where(
                Member.user_id == changed_user_id,
                Member.company_id == company_id
            ).values({"is_staff": new_status}))
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't request invite")
        return SuccessfulResult(status="changed")

    @staticmethod
    async def get_all_companies(
            session: AsyncSession,
            limit: int = 200,
            offset: int = 0
    ) -> list[CompanyResponseSchema]:
        companies = await session.execute(select(Company).where(Company.hidden == False).limit(limit).offset(offset))
        return [CompanyResponseSchema(name=c.name, description=c.description) for c in companies.scalars()]
