import logging

from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, FSInputFile


async def edit_message(message: Message, text: str, reply_markup=None, photo_path: str = None):
    try:
        if not photo_path:
            msg = await message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            msg = await message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=reply_markup)
            await message.delete()
        return msg

    except TelegramAPIError:
        if not photo_path:
            msg = await message.answer(text, reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            msg = await message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=reply_markup)
        return msg

    except Exception as e:
        logging.error(e)
