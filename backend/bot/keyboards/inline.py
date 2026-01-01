from aiogram.types import (
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

inline_kb = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text="Launch Web App", web_app=WebAppInfo(url="https://example.com")),
).adjust(1).as_markup()
