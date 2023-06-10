from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_phone_number() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row()
    kb.add(KeyboardButton('Отправить номер телефона', request_contact=True))
    return kb


async def registration_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    kb.row()
    kb.add(KeyboardButton('Получить помощь по регистрации'))
    kb.add(KeyboardButton('Допустил ошибку/Начать заново'))
    return kb


async def regular_user_start_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    kb.row()
    kb.add(KeyboardButton('Помощь'))
    kb.add(KeyboardButton('Мероприятия клуба'))
    return kb
