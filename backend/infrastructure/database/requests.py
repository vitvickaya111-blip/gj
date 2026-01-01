from dataclasses import dataclass

from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.database import setup as database_setup
from infrastructure.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    sessionmaker: async_sessionmaker

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.sessionmaker)


def get_database_repo() -> RequestsRepo:
    if database_setup.async_session is None:
        raise RuntimeError("async_session not initialized")
    return RequestsRepo(sessionmaker=database_setup.async_session)
