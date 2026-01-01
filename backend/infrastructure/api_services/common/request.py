import asyncio
from typing import Any, Dict, Optional

import httpx

from settings import settings, logger

semaphore = asyncio.Semaphore(5)
request_queue = asyncio.Queue()


async def make_request(
        method: str,
        route: str,
        host: Optional[str],
        port: Optional[str],
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any] | str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 180.0,
) -> Any:
    """
        Выполняет HTTP-запрос с использованием указанного метода на заданный маршрут.

        :param method: HTTP-метод ('GET' или 'POST').
        :param route: Маршрут для запроса.
        :param host: (Необязательно) Host сервера для запроса.
        :param port: (Необязательно) Порт сервера для запроса.
        :param params: (Необязательно) Словарь параметров запроса для GET-запросов.
        :param data: (Необязательно) Словарь данных формы для POST-запросов.
        :param json: (Необязательно) Словарь для тела запроса в формате JSON для POST-запросов.
        :param headers: (Необязательно) Словарь заголовков запроса.
        :param timeout: (Необязательно) Время ожидания ответа от сервера в секундах.
        :return: Объект Response от httpx.
        """
    async with semaphore:
        try:
            async with httpx.AsyncClient() as client:
                prefix = "http://"
                url = f"{prefix}{host}:{port}/{route}"

                if method.upper() == 'GET':
                    response = await client.get(url=url, params=params, headers=headers, timeout=timeout)
                elif method.upper() == 'POST':
                    response = await client.post(url=url, data=data, json=json, headers=headers, timeout=timeout)
                else:
                    raise ValueError("Метод должен быть 'GET' или 'POST'.")

                # Проверяем, что ответ от сервера успешный (код состояния 2xx)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None

            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")

        except httpx.NetworkError as e:
            logger.error(f"Network error occurred: {e}")

        except httpx.TimeoutException as e:
            logger.error(f"Timeout occurred: {e}")

        except httpx.RemoteProtocolError as e:
            logger.error(f"Remote protocol error occurred: {e}")

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")


async def worker():
    while True:
        method, route, params, data, json, headers = await request_queue.get()
        try:
            response = await make_request(method, route, params=params, data=data, json=json, headers=headers)
            logger.info(f"Response: {response}")
        except Exception as e:
            logger.error(f"Error occurred while processing request: {e}")
        finally:
            request_queue.task_done()


async def start_workers():
    for _ in range(3):
        asyncio.create_task(worker())
