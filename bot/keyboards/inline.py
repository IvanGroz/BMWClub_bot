from aiogram.types import *


async def start_reg_message() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Зарегистрироваться", callback_data='register'))
    return kb

