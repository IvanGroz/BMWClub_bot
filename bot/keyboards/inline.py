from aiogram.types import *
from aiogram.utils.callback_data import CallbackData


async def start_reg_message() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Зарегистрироваться", callback_data='register'))
    return kb


async def car_number_plate_non_rus() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Мой гос.номер другого формата", callback_data='non_rus_plate'))
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


question_answer_callbackdata = CallbackData('answer', 'user_id')


async def question_answer(user_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row()
    kb.insert(InlineKeyboardButton("Ответить на вопрос", url="tg://user?id={}".format(user_id)))
    kb.insert(InlineKeyboardButton("Отвечен!", callback_data=question_answer_callbackdata.new(user_id)))
    return kb


async def question_delete() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row()
    kb.insert(InlineKeyboardButton("Удалить вопрос",
                                   callback_data='delete_question'))
    return kb


async def end_create_event() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row()
    kb.insert(InlineKeyboardButton("Все правильно!", callback_data="correct_event"))
    kb.insert(InlineKeyboardButton("Создать заново!", callback_data='recreate_event'))
    return kb
