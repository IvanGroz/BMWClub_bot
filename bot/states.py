# тут содержатся состояния для машины состояний
from typing import Final

from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterUser(StatesGroup):
    INSERT_SURNAME: Final = State()  # Состояние при котором принимается Фамилия
    INSERT_NAME: Final = State()  # Состояние при котором принимается Имя
    INSERT_PATRONYMIC: Final = State()  # Состояние при котором принимается Отчество
    INSERT_ABOUT: Final = State()  # Состояние при котором принимается о том чем занимается пользователь
    INSERT_CAR_PHOTO: Final = State()  # Состояние при котором принимается Фото Авто
    INSERT_NUMBER_PLATE: Final = State()  # Состояние при котором принимается Гос. Номер Авто
    INSERT_NON_RUS_PLATE: Final = State()  # Состояние при котором принимается иностранный Гос. Номер Авто
    INSERT_PARTNER_BUSINESS: Final = State()  # Состояние при котором принимается Информация о партнерстве
    NEUTRAL: Final = State()
    HELP_QUESTION: Final = State()


class CreateEvent(StatesGroup):
    INSERT_TITLE: Final = State()  # Состояние при котором принимается заголовок события
    INSERT_DESCRIPTION: Final = State()  # Состояние при котором принимается описание
    INSERT_LOCATION: Final = State()  # Состояние при котором принимается место проведения
    INSERT_DATA: Final = State()  # Состояние при котором принимается дата проведения
    INSERT_TIME: Final = State()  # Состояние при котором принимается время проведения
    FINISH_CREATE:Final = State() # Состояние при котором должно завершаться создание мероприятия
