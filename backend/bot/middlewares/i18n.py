from typing import Optional, Dict, Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, I18nMiddleware
from babel import Locale

from infrastructure.database.models import User


class CustomI18nMiddleware(I18nMiddleware):
    """
    Custom I18n middleware.

    Instruction:
    Запускаем первый раз
    1. Вытаскиваем тексты из файлов (он сам находит)
    pybabel extract . -o locales/messages.pot
    2. Создаем папку для перевода на английский
    pybabel init -i locales/messages.pot -d locales -D messages -l en
    3. То же, на русский
    pybabel init -i locales/messages.pot -d locales -D messages -l ru
    4. Переводим, а потом собираем переводы
    pybabel compile -d locales -D messages


    Обновляем переводы
    1. Вытаскиваем тексты из файлов, Добавляем текст в переведенные версии
    pybabel extract . -o locales/messages.pot
    pybabel update -d locales -D messages -i locales/messages.pot
    3. Вручную делаем переводы, а потом Собираем
    pybabel compile -d locales -D messages
    """

    def __init__(
            self,
            i18n: I18n,
            i18n_key: Optional[str] = "i18n",
            middleware_key: str = "i18n_middleware",
    ) -> None:
        super().__init__(i18n=i18n, i18n_key=i18n_key, middleware_key=middleware_key)

        if Locale is None:  # pragma: no cover
            raise RuntimeError(
                f"{type(self).__name__} can be used only when Babel installed\n"
                "Just install Babel (`pip install Babel`) "
                "or aiogram with i18n support (`pip install aiogram[i18n]`)"
            )

    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        if Locale is None:  # pragma: no cover
            raise RuntimeError(
                f"{type(self).__name__} can be used only when Babel installed\n"
                "Just install Babel (`pip install Babel`) "
                "or aiogram with i18n support (`pip install aiogram[i18n]`)"
            )

        user: User = data["user"]
        return user.language
