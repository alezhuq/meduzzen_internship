from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

from app.schemas.user_schemas import UserSchema
from app.schemas.core import SuccessfulResult
from app.db.services.userservice import UserService
from app.db.services.companyservice import CompanyService, InviteStatus
from app.api.dependencies.dependencies import get_repository, get_current_user, get_session
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema

router = APIRouter(
    prefix="/invite",
    tags=["invite"],
)


@router.post('/company/{company_id}', response_model=SuccessfulResult)
async def invite(
        company_id: int,
        invited_user_id: int,
        current_user: UserSchema = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
) -> SuccessfulResult:
    try:
        result = await CompanyService.invite_to_company(
            session=session,
            company_id=company_id,
            user_id=invited_user_id,
            owner_id=current_user.id)
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result


@router.post('/company/{company_id}/request', response_model=SuccessfulResult)
async def request_invite(
        company_id: int,
        current_user: UserSchema = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
) -> SuccessfulResult:
    result = await CompanyService.request_invite(
        session=session,
        company_id=company_id,
        user_id=current_user.id
    )
    return result


@router.put('/company/{company_id}/reply', response_model=SuccessfulResult)
async def owner_reply_to_invite(
        user_id: int,
        company_id: int,
        reply: InviteStatus,
        session: AsyncSession = Depends(get_session),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await CompanyService.reply_to_invite_request(
            session=session,
            user_id=user_id,
            company_id=company_id,
            owner_id=current_user.id,
            reply=reply
        )
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result


@router.put('/company/{company_id}/respond', response_model=SuccessfulResult)
async def user_reply_to_invite(
        company_id: int,
        reply: bool,
        session: AsyncSession = Depends(get_session),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await CompanyService.accept_decline_invite(
            session=session,
            user_id=current_user.id,
            company_id=company_id,
            accept=reply
        )
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="can't reply to invite")
    return result

