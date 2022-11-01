from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.schemas.user_schemas import UserSchema, SuccessfulResult
from app.db.services.userservice import UserService
from app.db.services.companyservice import CompanyService, InviteStatus
from app.api.dependencies.dependencies import get_repository, get_current_user
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema

router = APIRouter(
    prefix="/invite",
    tags=["invite"],
)


@router.post('/company/{company_id}', response_model=SuccessfulResult)
async def invite(
        company_id: int,
        invited_user_id: int,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    is_owner = await company_service.check_owner(company_id=company_id, user_id=current_user.id)
    if not is_owner:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="you do not have permissions to create this invitation"
        )
    result = await company_service.invite_to_company(company_id=company_id, user_id=invited_user_id)
    return result


@router.post('/company/{company_id}/request', response_model=SuccessfulResult)
async def request_invite(
        company_id: int,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    result = await company_service.request_invite(company_id=company_id, user_id=current_user.id)
    return result


@router.put('/company/{company_id}/reply')
async def reply_to_invite(
        user_id: int,
        company_id: int,
        reply: InviteStatus,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    is_owner = await company_service.check_owner(company_id=company_id, user_id=current_user)
    if not is_owner:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="you do not have permissions to reply to this invite"
        )
    result = await company_service.reply_to_invite_request(user_id=user_id, company_id=company_id, reply=reply)
    return result


@router.put('/company/{company_id}/respond')
async def reply_to_invite(
        company_id: int,
        reply: bool,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:

    result = await company_service.accept_decline_invite(user_id=current_user.id, company_id=company_id, reply=reply)
    return result

