from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from infrastructure.database.requests import RequestsRepo

router = Router()


@router.message(Command('admin'))
async def admin_start(message: Message, repo: RequestsRepo):
    users_count = await repo.users.count_all()
    await message.answer(f"Привет, админ!\n\nВсего пользователей: {users_count}")
