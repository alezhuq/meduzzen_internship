from pydantic import BaseModel


class QuizSchema(BaseModel):
    name: str
    description: str


class QuestionSchema(BaseModel):
    quiz_id: int
    name: str


class AnswerSchema(BaseModel):
    question_id: int
    answer: str
    is_right: bool


class AnswerCreateSchema(BaseModel):
    answer: str
    is_right: bool


class QuestionCreateSchema(BaseModel):
    name: str
    answers: list[AnswerCreateSchema]


class QuizCreateSchema(BaseModel):
    company_id: int
    name: str
    description: str
    questions: list[QuestionCreateSchema]
