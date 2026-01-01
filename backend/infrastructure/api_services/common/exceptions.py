import logging
from http import HTTPStatus
from typing import Callable, Any, Union
from uuid import UUID

import httpx
from fastapi import HTTPException


async def generic_exception_handler(
        async_func: Callable[..., Any] = None,
        sync_func: Callable[..., Any] = None,
        response_model=None,
        args=(),
        kwargs=None
) -> Any:
    """
    Универсальный обработчик исключений для асинхронных функций.

    :param async_func: Асинхронная функция, для которой необходимо обработать исключения.
    :param sync_func: Синхронная функция, для которой необходимо обработать исключения.
    :param response_model: Модель ответа.
    :param args: Аргументы, передаваемые в функцию.
    :param kwargs: Именованные аргументы, передаваемые в функцию.
    :return: Результат выполнения функции.
    :raises: HTTPException с кодом 500 в случае возникновения исключения.

    """
    if kwargs is None:
        kwargs = {}
    try:
        if async_func:
            result = await async_func(*args, **kwargs)
        else:
            result = sync_func(*args, **kwargs)

        if result is not None:
            if response_model:
                if isinstance(result, list):
                    return [response_model.model_validate(obj, from_attributes=True) for obj in result]

                return response_model.model_validate(result, from_attributes=True)
            return result

        else:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Object not found"
            )

    except HTTPException as http_exc:
        logging.error(f"HTTP error occurred: {http_exc}")
        raise http_exc

    except httpx.HTTPStatusError as http_exc:
        logging.error(f"HTTP error occurred: {http_exc}", exc_info=True)
        raise HTTPException(status_code=http_exc.response.status_code, detail=str(http_exc))

    except httpx.RequestError as req_exc:
        logging.error(f"Request error occurred: {req_exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Network error or connection timeout")

    except Exception as exc:
        logging.error(f"An error occurred: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


class AppBaseError(Exception):
    pass


class ResourceNotFound(HTTPException):
    def __init__(self, resource_id: Union[UUID, int, str], resource_name: Union[UUID, int, str] = "Resource") -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"{resource_name} {resource_id} was not found"
        )


class ResourceConflict(HTTPException):
    def __init__(self, resource_name: Union[UUID, int, str] = "Resource") -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            detail=f"{resource_name} already exists."
        )


class BadRequest(HTTPException):
    source = "Source"
    relation = "Relation"

    def __init__(self) -> None:
        super().__init__(
            HTTPStatus.CONFLICT,
            f"Provided {self.source} id or {self.relation} id not found in database.",
        )


class ElasticsearchRepositoryError(AppBaseError):
    pass


class AuthIsUnavailableError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            HTTPStatus.SERVICE_UNAVAILABLE,
            "Authorization service is unavailable. Please try again later.",
        )
