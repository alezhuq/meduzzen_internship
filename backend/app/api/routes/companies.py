from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Params, paginate, Page
from fastapi_pagination.bases import AbstractPage
from starlette.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from app.schemas.user_schemas import UserSchema, SuccessfulResult
from app.db.services.userservice import UserService
from app.db.services.companyservice import CompanyService
from app.api.dependencies.dependencies import get_repository, get_current_user
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema
from app.core.exceptions import NotFoundException

router = APIRouter(
    prefix="/company",
    tags=["company"],
)
DEFAULT_PAGINATION_PAGE = 1
DEFAULT_PAGINATION_SIZE = 10


@router.get("/all", response_model=Page[CompanyResponseSchema])
async def get_all_companies(
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user),
        page: int = DEFAULT_PAGINATION_PAGE,
        size: int = DEFAULT_PAGINATION_SIZE,
) -> AbstractPage[CompanyResponseSchema]:
    companies = await company_service.get_all_companies()
    if not companies:
        raise NotFoundException(detail="no companies found")
    return paginate(companies, Params(page=page, size=size))


@router.post("/{company_id}", response_model=SuccessfulResult)
async def create_new_company(
        new_company: CompanyCreatechema,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    result = await company_service.create_company(user=current_user, new_company=new_company)
    if result is None:
        raise HTTPException(status_code=422, detail="can't create company")
    return result


@router.put("/{company_id}/update/status", response_model=SuccessfulResult)
async def update_company_status(
        company_id: int,
        hidden: bool,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await company_service.change_visibility(
            user_id=current_user.id,
            company_id=company_id,
            new_status=hidden,
            owner_id=current_user.id
        )
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result


@router.put("/{company_id}/update/details", response_model=SuccessfulResult)
async def update_company_details(
        company_id: int,
        details: CompanyResponseSchema,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await company_service.change_name_description(
            user_id=current_user.id,
            company_id=company_id,
            company=details,
            owner_id=current_user.id
        )
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result


@router.put("/{company_id}/update/details", response_model=SuccessfulResult)
async def update_staff_status(
        user_id: int,
        company_id: int,
        is_staff: bool,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await company_service.change_staff_status(
            company_id=company_id,
            user_id=current_user.id,
            changed_user_id=user_id,
            new_status=is_staff,
            owner_id=current_user.id
        )
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result


@router.delete("/{company_id}", response_model=SuccessfulResult)
async def delete_company(
        company_id: int,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await company_service.delete_company(company_id=company_id, owner_id=current_user.id)
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result


@router.delete("/{company_id}/member/{member_id}", response_model=SuccessfulResult)
async def kick_member(
        member_id: int,
        company_id: int,
        company_service: CompanyService = Depends(get_repository(CompanyService)),
        current_user: UserSchema = Depends(get_current_user)
) -> SuccessfulResult:
    try:
        result = await company_service.kick_from_company(
            user_id=current_user.id,
            member_id=member_id,
            company_id=company_id,
            owner_id=current_user.id
        )
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="you don't have permissions to do this")
    return result
