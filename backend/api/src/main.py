from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker

from api.src.users.v1.user import router as user_router
from infrastructure.api_services.common.cors import setup_cors
from infrastructure.database import setup as database
from infrastructure.database import setup as database_setup
from infrastructure.database.requests import RequestsRepo
from settings import settings, logger


@asynccontextmanager
async def lifespan(App: FastAPI):  # noqa
    database.redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    # Initialize Cache and Limiter
    await initialize_cache_and_limiter()
    # Initialize database
    await initialize_database()
    logger.info("Application initialized")
    yield
    await database.redis.close()
    await FastAPILimiter.close()


app = FastAPI(
    lifespan=lifespan,
    title=" API",
    description="API для выполнения операций с пользователями.",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    version=settings.app_version,
)


@app.get("/ping")
async def pong() -> dict[str, str]:
    return {"ping": "pong!"}


@app.get("/version")
@cache(expire=600)
def get_version() -> dict[str, str]:
    return {"version": settings.service.app_version}


app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])

setup_cors(app, settings)
add_pagination(app)


async def initialize_cache_and_limiter():
    database.redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    FastAPICache.init(RedisBackend(database.redis), prefix="fastapi-cache")
    await FastAPILimiter.init(database.redis)


async def initialize_database():
    database.init_database(settings)
    await startup(database.async_session)


async def startup(session_pool: async_sessionmaker) -> None:
    repo = RequestsRepo(sessionmaker=database_setup.async_session)
