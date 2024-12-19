from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine(
    'postgresql+asyncpg://postgres:admin@localhost:5432/fastapi_ex',
    echo=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
