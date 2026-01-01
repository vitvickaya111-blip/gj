import asyncio
import logging
import os

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio.client import Redis
from redis.connection import ConnectionPool
from sqlalchemy.ext.asyncio import async_sessionmaker

from handlers import routers_list
from infrastructure.database.setup import create_engine, create_session_pool
from middlewares.config import ConfigMiddleware
from middlewares.database import DatabaseMiddleware
from middlewares.i18n import CustomI18nMiddleware
from services import broadcaster
from settings import get_app_settings
from settings.app_settings import AppSettings
from utils.set_bot_commands import set_default_commands, set_admin_commands


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids[:1], "Бот запущен!")
    await set_default_commands(bot)
    await set_admin_commands(bot, admin_ids)


def register_global_middlewares(
        dp: Dispatcher,
        settings: AppSettings,
        i18n: I18n = None,
        async_session: async_sessionmaker = None,
        redis: Redis = None,
        apscheduler: AsyncIOScheduler = None,
):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param apscheduler: The apscheduler instance.
    :param i18n: The i18n instance.
    :param redis: The redis instance.
    :param dp: The dispatcher instance.
    :param async_session: The async session instance.
    :type dp: Dispatcher
    :param settings: The configuration object from the loaded configuration.
    :return: None
    """
    bot_middleware = [
        ConfigMiddleware(settings, apscheduler),
        DatabaseMiddleware(async_session, redis),
        CustomI18nMiddleware(i18n),
    ]

    channel_middleware = [
        ConfigMiddleware(settings, apscheduler),
    ]

    for middleware_type in bot_middleware:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)
        dp.my_chat_member.outer_middleware(middleware_type)

    for middleware_type in channel_middleware:
        dp.channel_post.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage():
    """
    Return storage based on the provided configuration.

    Returns:
        Storage: The storage object based on the configuration.

    """
    return MemoryStorage()


async def main():
    setup_logging()

    scheduler = AsyncIOScheduler()
    scheduler.start()
    settings = get_app_settings()

    storage = get_storage()
    bot = Bot(token=settings.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)

    relative_path = os.path.join(os.getcwd(), "bot", "locales")
    i18n = I18n(path=relative_path, default_locale="ru", domain="messages")

    dp.include_routers(*routers_list)

    engine = create_engine(settings.postgres)
    session_pool = create_session_pool(engine)

    connection_pool = ConnectionPool.from_url(settings.redis.dsn)
    redis = Redis(connection_pool=connection_pool)

    register_global_middlewares(dp, settings, i18n, session_pool, redis, scheduler)

    await on_startup(bot, settings.bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот остановлен!")
