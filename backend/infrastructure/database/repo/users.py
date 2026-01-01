from typing import Optional, Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    def __init__(self, sessionmaker: async_sessionmaker):
        super().__init__(sessionmaker, User)  # noqa

    async def get_or_create(
            self,
            user_id: Union[int, str],
            first_name: str,
            last_name: Optional[str],
            language: str,
            username: Optional[str] = None,
            **kwargs
    ) -> User:
        async with self.sessionmaker() as session:
            insert_stmt = (
                insert(User)
                .values(
                    id=int(user_id),
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language=language,
                    **kwargs
                )
                .on_conflict_do_update(
                    index_elements=[User.id],
                    set_=dict(
                        language=language,
                        **kwargs
                    ),
                )
                .returning(User)
            )
            result = await session.execute(insert_stmt)
            await session.commit()
            return result.scalar_one_or_none()
