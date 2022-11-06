from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from app.db.models.base import session
from app.core.exceptions import AlreadyExistsException, NotFoundException
from .base import BaseService
from app.db.models.company import Company
from app.db.models.quiz import Quiz, Question, Answer
from app.schemas.company_schemas import CompanySchema, CompanyResponseSchema, CompanyCreatechema, MemberSchema
from app.schemas.quiz_schemas import QuizCreateSchema, AnswerCreateSchema, QuestionCreateSchema, QuizSchema
from app.schemas.user_schemas import UserSchema
from app.schemas.core import SuccessfulResult
from .companyservice import check_owner, check_staff


class QuizService(BaseService):

    async def create_answers(self, *, question_id: int, answers: list[AnswerCreateSchema]):
        try:
            answer_list = [
                Answer(question_id=question_id, answer=answer.answer, is_right=answer.is_right)
                for answer in answers
            ]

            session.add_all(answer_list)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @check_staff
    async def create_questions(
            self, *, staff_id: int, company_id: int, quiz_id: int, questions: list[QuestionCreateSchema]
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
                session.commit()

                created_question = session.query(Question).filter_by(name=question.name).first()
                await self.create_answers(question_id=created_question.id, answers=question.answers)
            except Exception as e:
                session.rollback()
                raise e

        return SuccessfulResult(status="created")

    @check_staff
    async def create_quiz(self, *, staff_id: int, company_id: int, quiz: QuizCreateSchema) -> SuccessfulResult:
        try:
            new_quiz = Quiz(company_id=company_id, name=quiz.name, description=quiz.description)
            session.add(new_quiz)
            session.commit()
            created_quiz = session.query(Quiz).filter_by(name=new_quiz.name).first()
            if len(quiz.questions) < 2:
                raise HTTPException(HTTP_400_BAD_REQUEST, detail="there must be at least 2 questions")
            res = await self.create_questions(
                staff_id=staff_id,
                company_id=company_id,
                quiz_id=created_quiz.id,
                questions=quiz.questions
            )

        except Exception:
            session.rollback()
            raise HTTPException(HTTP_400_BAD_REQUEST, detail="wrong data")

        return SuccessfulResult(status="created")

    @check_staff
    async def delete_question(self, *, staff_id: int, company_id: int, quetion_id: int) -> SuccessfulResult:
        try:
            selected_question = session.query(Question).filter_by(id=quetion_id).first()
            session.delete(selected_question)
            session.commit()

        except Exception:
            raise NotFoundException(detail="question was not found")
        return SuccessfulResult(status="deleted")

    @check_staff
    async def delete_quiz(self, *, staff_id: int, company_id: int, quiz_id: int) -> SuccessfulResult:
        try:
            selected_quiz = session.query(Quiz).filter_by(id=quiz_id).first()
            session.delete(selected_quiz)
            session.commit()

        except Exception:
            raise NotFoundException(detail="quiz was not found")
        return SuccessfulResult(status="deleted")

    @check_staff
    async def get_all_quizzes(self, *, staff_id: int, company_id: int,) -> list[QuizSchema]:
        try:
            quizzes = session.query(Quiz).filter_by(company_id=company_id).all()
        except Exception:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="bad request")

        return [QuizSchema(name=quiz.name, description=quiz.description) for quiz in quizzes]
