from fastapi import Depends

from infrastructure.database.requests import RequestsRepo, get_database_repo


class UserService:
    def __init__(self, repo: RequestsRepo):
        self.repo = repo


def get_user_service(
        repo: RequestsRepo = Depends(get_database_repo),
) -> UserService:
    return UserService(repo=repo)
