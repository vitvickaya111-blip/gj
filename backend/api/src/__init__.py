import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from settings import settings

logger = logging.getLogger(__name__)
bot = Bot(token=settings.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
