from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Params, paginate, Page
from fastapi_pagination.bases import AbstractPage
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from app.schemas.user_schemas import UserSchema
from app.db.services.quizservice import QuizService
from app.schemas.core import SuccessfulResult
from app.db.services.userservice import UserService
from app.db.services.companyservice import CompanyService
from app.api.dependencies.dependencies import get_repository, get_current_user, get_session
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema
from app.core.exceptions import NotFoundException
from app.schemas.quiz_schemas import QuizCreateSchema, QuestionCreateSchema, QuizSchema

router = APIRouter(
    prefix="/company/{company_id}/quiz",
    tags=["quiz"],
)

DEFAULT_PAGINATION_PAGE = 1
DEFAULT_PAGINATION_SIZE = 10


@router.get("/all", response_model=Page[QuizSchema])
async def get_all_quizzes(
        company_id: int,
        page: int = DEFAULT_PAGINATION_PAGE,
        size: int = DEFAULT_PAGINATION_SIZE,
        session: AsyncSession = Depends(get_session),
        current_user: UserSchema = Depends(get_current_user),
) -> AbstractPage[QuizSchema]:
    quizzes = await QuizService.get_all_quizzes(
        session=session,
        company_id=company_id,
        staff_id=current_user.id,
    )
    if not quizzes:
        raise NotFoundException(detail="no quizzes found")
    return paginate(quizzes, Params(page=page, size=size))


@router.post("/", response_model=SuccessfulResult)
async def create_quiz(
        company_id: int,
        new_quiz: QuizCreateSchema,
        current_user: UserSchema = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
) -> SuccessfulResult:
    result = await QuizService.create_quiz(
        session=session, staff_id=current_user.id, company_id=company_id, quiz=new_quiz
    )
    return result


@router.delete("/", response_model=SuccessfulResult)
async def delete_quiz(
        company_id: int,
        quiz_id: int,
        current_user: UserSchema = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
) -> SuccessfulResult:
    result = await QuizService.delete_quiz(
        session=session,
        staff_id=current_user.id,
        company_id=company_id,
        quiz_id=quiz_id,
    )
    return result


@router.post("/{quiz_id}/", response_model=SuccessfulResult)
async def add_questions(
        company_id: int,
        quiz_id: int,
        questions: list[QuestionCreateSchema],
        current_user: UserSchema = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),

) -> SuccessfulResult:
    result = await QuizService.create_questions(
        session=session,
        staff_id=current_user.id,
        company_id=company_id,
        quiz_id=quiz_id,
        questions=questions
    )
    return result


@router.delete("/{quiz_id}/", response_model=SuccessfulResult)
async def delete_question(
        company_id: int,
        question_id: int,
        current_user: UserSchema = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
) -> SuccessfulResult:
    result = await QuizService.delete_question(
        session=session,
        staff_id=current_user.id,
        company_id=company_id,
        question_id=question_id,
    )
    return result
