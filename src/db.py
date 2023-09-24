from typing import AsyncGenerator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, TIMEZONE


DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
Base = declarative_base()

metadata = MetaData()

SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(
    SYNC_DATABASE_URL, connect_args={"options": f"-c timezone={TIMEZONE}"}
)
session_maker = sessionmaker(engine)

aengine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(
    aengine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
