from aiogram.types import *
from aiogram.utils import *


async def start_reg_message() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Зарегистрироваться", callback_data='register'))
    return kb
