from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.models.base import session
from app.core.exceptions import NotFoundException
from .base import BaseService
from app.db.models.quiz import Quiz, Question, Answer
from app.schemas.quiz_schemas import QuizCreateSchema, AnswerCreateSchema, QuestionCreateSchema, QuizSchema
from app.schemas.core import SuccessfulResult
from .companyservice import check_staff


class QuizService(BaseService):

    @staticmethod
    async def create_answers(*, session: AsyncSession, question_id: int, answers: list[AnswerCreateSchema]) -> None:
        try:
            answer_list = [
                Answer(question_id=question_id, answer=answer.answer, is_right=answer.is_right)
                for answer in answers
            ]

            session.add_all(answer_list)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

    @staticmethod
    @check_staff
    async def create_questions(
            *, session: AsyncSession, staff_id: int, company_id: int, quiz_id: int,
            questions: list[QuestionCreateSchema]
    ) -> SuccessfulResult:

        for question in questions:
            try:
                is_right_answer = 0
                if len(question.answers) < 2:
                    raise HTTPException(HTTP_400_BAD_REQUEST, detail="there must be at least 2 answers")

                for answer in question.answers:
                    is_right_answer += int(answer.is_right)
                if not is_right_answer or is_right_answer > 1:
                    raise HTTPException(HTTP_400_BAD_REQUEST, detail="incorrect amount of right answers")
                new_question = Question(quiz_id=quiz_id, name=question.name)

                session.add(new_question)
                await session.commit()

                created_question_request = await session.execute(select(Question).where(Question.name == question.name))
                created_question = created_question_request.scalars().first()
                await QuizService.create_answers(session=session, question_id=created_question.id,
                                                 answers=question.answers)
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"{str(e)}")

        return SuccessfulResult(status="created")

    @staticmethod
    @check_staff
    async def create_quiz(*, session: AsyncSession, staff_id: int, company_id: int,
                          quiz: QuizCreateSchema) -> SuccessfulResult:
        try:
            new_quiz = Quiz(company_id=company_id, name=quiz.name, description=quiz.description)
            session.add(new_quiz)
            await session.commit()
            created_quiz_request = await session.execute(select(Quiz).where(Quiz.name == new_quiz.name))
            created_quiz = created_quiz_request.scalars().first()
            if len(quiz.questions) < 2:
                raise HTTPException(HTTP_400_BAD_REQUEST, detail="there must be at least 2 questions")
            res = await QuizService.create_questions(
                session=session,
                staff_id=staff_id,
                company_id=company_id,
                quiz_id=created_quiz.id,
                questions=quiz.questions
            )

        except Exception:
            await session.rollback()
            raise HTTPException(HTTP_400_BAD_REQUEST, detail="wrong data")

        return SuccessfulResult(status="created")

    @staticmethod
    @check_staff
    async def delete_question(*, session: AsyncSession, staff_id: int, company_id: int,
                              quetion_id: int) -> SuccessfulResult:
        try:
            selected_question_request = await session.execute(select(Question).where(Question.id == quetion_id))
            selected_question = selected_question_request.scalars().first()
            await session.delete(selected_question)
            await session.commit()

        except Exception:
            await session.rollback()
            raise NotFoundException(detail="question was not found")
        return SuccessfulResult(status="deleted")

    @staticmethod
    @check_staff
    async def delete_quiz(*, session: AsyncSession, staff_id: int, company_id: int,
                          quiz_id: int) -> SuccessfulResult:
        try:
            selected_quiz_request = await session.execute(select(Quiz).where(Quiz.id == quiz_id))
            selected_quiz = selected_quiz_request.scalars().first()
            await session.delete(selected_quiz)
            await session.commit()

        except Exception:
            await session.rollback()
            raise NotFoundException(detail="quiz was not found")
        return SuccessfulResult(status="deleted")

    @staticmethod
    @check_staff
    async def get_all_quizzes(
            *,
            session: AsyncSession,
            staff_id: int,
            company_id: int,
            limit: int = 200,
            offset: int = 0
    ) -> list[QuizSchema]:
        try:
            quizzes = await session.execute(
                select(Quiz).where(Quiz.company_id == company_id).limit(limit).offset(offset)
            )

        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="bad request")

        return [QuizSchema(name=quiz.name, description=quiz.description) for quiz in quizzes.scalars()]
