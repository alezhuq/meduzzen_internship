from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import DATABASE_URL


BaseModel = declarative_base()

engine = create_async_engine(
    str(DATABASE_URL),
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
session = async_session()