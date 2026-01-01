from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings.app_settings import AppSettings
from settings.db_settings import DatabaseSettings

async_session: async_sessionmaker | None = None
redis: None | Redis = None


def create_engine(db: DatabaseSettings, echo=False):
    engine = create_async_engine(
        db.construct_sqlalchemy_url,
        query_cache_size=1200,
        pool_size=20,
        max_overflow=200,
        future=True,
        echo=echo,
    )
    return engine


def create_session_pool(engine):
    session_pool = async_sessionmaker(bind=engine, expire_on_commit=False)
    return session_pool


def init_database(settings: AppSettings) -> None:
    global async_session

    engine = create_engine(settings.postgres)
    async_session = create_session_pool(engine)


async def get_db() -> AsyncGenerator[None, AsyncSession]:
    global async_session

    if async_session is None:
        return

    async with async_session() as db:
        yield db
