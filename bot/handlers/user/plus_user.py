from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import *

from bot.filters.main import *
from bot.keyboards import birthday_slider
from bot.keyboards.birthday_slider import BirthdaySlider
from bot.database import database as db

slider: BirthdaySlider


async def birthday_slider_start(message: Message):
    bot: Bot = message.bot
    birthdays = await db.get_users_birthday(14)
    text: str = 'В эту дату день рождения у:'
    for birthday in birthdays[0][0]:  # [номер дня][0 - пользователи , 1 - дата (месяц и день)]
        text += '\n[{} {} {}](tg://user?id={})\, исполняется {} лет '.format(birthday[1],
                                                                             birthday[2],
                                                                             birthday[3],
                                                                             birthday[0],
                                                                             birthday[4])
        global slider
        slider = BirthdaySlider(birthdays)
    await bot.send_message(message.chat.id, text, 'MarkdownV2',
                           reply_markup=await slider.get_slider_markup())


async def birthday_slider_callback(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    await slider.selection(callback_query, callback_data)


def register_user_plus_handlers(dp: Dispatcher) -> None:
    # handlers
    dp.register_message_handler(birthday_slider_start, IsPlusUser(), content_types=['text'], text='14')
    # callbacks
    dp.register_callback_query_handler(birthday_slider_callback, IsPlusUser(), birthday_slider.slider_callback.filter())
