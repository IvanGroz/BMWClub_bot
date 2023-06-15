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
    kb.row(KeyboardButton('Получить помощь/Задать вопрос'), KeyboardButton('Мероприятия клуба'))
    return kb


async def plus_user_start_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    kb.row(KeyboardButton('Дни рождения'), KeyboardButton('Мероприятия клуба'))
    kb.row(KeyboardButton('Получить помощь/Задать вопрос'))
    return kb


async def admin_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    kb.row(KeyboardButton('Дни рождения'), KeyboardButton('Мероприятия клуба'))
    kb.row(KeyboardButton('Инструкции'), KeyboardButton('Рассылка'))
    kb.row(KeyboardButton('Информация о пользователях'), KeyboardButton('Редактировать пользователя'))
    return kb


async def birthday_menu(notif_on) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton('Показать ДР на ближайшие 14 дней'),
           KeyboardButton('Отключить уведомления о ДР' if notif_on[0] else 'Включить уведомления о ДР')
           )
    kb.row(KeyboardButton('Узнать день рождения по ФИО'))
    return kb


async def event_admin_menu(notif_on) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton('Ближайшие мероприятия'),
           KeyboardButton('Отключить уведомления' if notif_on[0] else 'Включить уведомления'))
    kb.row(KeyboardButton('Создать мероприятие'))
    return kb


async def event_menu(notif_on) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton('Ближайшие мероприятия'),
           KeyboardButton('Отключить уведомления' if notif_on[0] else 'Включить уведомления'))
    return kb


async def users_info_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton('Найти пользователя по Гос.Номеру'),
        KeyboardButton('Найти пользователя по ФИО')
    )
    kb.row(KeyboardButton('Получить данные о всех пользователях'))
    return kb
