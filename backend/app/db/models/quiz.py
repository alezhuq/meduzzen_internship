import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .base import BaseModel


class Quiz(BaseModel):
    __tablename__ = "quiz"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    company_id = sa.Column(sa.Integer, sa.ForeignKey("company.id", ondelete="CASCADE"), primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    passed_per_day = sa.Column(sa.Integer)
    company = relationship("Company", back_populates="quizzes")


class Question(BaseModel):
    __tablename__ = "question"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    quiz_id = sa.Column(sa.Integer, sa.ForeignKey("quiz.id", ondelete="CASCADE"), primary_key=True)
    name = sa.Column(sa.String)
    answers = relationship("Answer", back_populates="question")


class Answer(BaseModel):
    __tablename__ = "answer"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    question_id = sa.Column(sa.Integer, sa.ForeignKey("question.id", ondelete="CASCADE"), primary_key=True)
    answer = sa.Column(sa.String)
    is_right = sa.Column(sa.Boolean, default=False)
    question = relationship("Question", back_populates="answers")
