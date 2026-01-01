from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from redis.asyncio.client import Redis

from infrastructure.database.requests import RequestsRepo


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, async_session, redis: Redis) -> None:
        self.async_session = async_session
        self.redis = redis

    async def __call__(
            self,
            handler: Callable[
                [Message | CallbackQuery | ChatMemberUpdated, Dict[str, Any]],
                Awaitable[Any],
            ],
            event: Message | CallbackQuery | ChatMemberUpdated,
            data: Dict[str, Any],
    ) -> Any:
        async with self.async_session() as session:
            repo = RequestsRepo(session)

            user = await repo.users.get_or_create(
                user_id=event.from_user.id,
                first_name=event.from_user.first_name,
                last_name=event.from_user.last_name,
                language=event.from_user.language_code,
                username=event.from_user.username
            )

            data["session"] = session
            data["repo"] = repo
            data["user"] = user

            result = await handler(event, data)

        return result
