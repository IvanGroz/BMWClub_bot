from aiogram import Bot

from bot.database import database as db
from bot.filters.main import *
from bot.keyboards import birthday_slider
from bot.keyboards.birthday_slider import BirthdaySlider
from bot.misc.formatting import format_birthday

slider: BirthdaySlider


async def birthday_slider_start(message: Message):
    bot: Bot = message.bot
    birthdays = await db.get_users_birthday(14)
    text: str = await format_birthday(birthdays, 0)
    global slider
    slider = BirthdaySlider(birthdays)
    await bot.send_message(message.chat.id, text, 'MarkdownV2', reply_markup=await slider.get_slider_markup())


async def birthday_slider_callback(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    await slider.selection(callback_query, callback_data)


def register_user_plus_handlers(dp: Dispatcher) -> None:
    # handlers
    dp.register_message_handler(birthday_slider_start, IsPlusUser(), content_types=['text'], text='14')
    # callbacks
    dp.register_callback_query_handler(birthday_slider_callback, IsPlusUser(), birthday_slider.slider_callback.filter())
