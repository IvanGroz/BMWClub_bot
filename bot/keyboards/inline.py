from aiogram.types import *


async def start_reg_message() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Зарегистрироваться", callback_data='register'))
    return kb


async def car_number_plate_non_rus() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Мой гос.номер другого формата /Не российский номер", callback_data='non_rus_plate'))
    return kb


async def partner_choice() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row()
    kb.insert(InlineKeyboardButton("Я хочу стать партнёром", callback_data='wanna_be_partner'))
    kb.insert(InlineKeyboardButton("Нет", callback_data='no_partner'))
    return kb


async def end_registration() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Завершить регистрацию", callback_data='end_registration'))
    return kb
