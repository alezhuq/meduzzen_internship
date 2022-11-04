from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from app.core.config import DATABASE_URL


BaseModel = declarative_base()

engine = create_engine(
    str(DATABASE_URL),
)

session = Session(engine)