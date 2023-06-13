from aiogram import Bot

from bot.database import database as db
from bot.filters.main import *
from bot.keyboards import birthday_slider
from bot.keyboards.birthday_slider import BirthdaySlider
from bot.misc.formatting import format_birthday
import bot.keyboards as kb

slider: BirthdaySlider


async def birthday_slider_start(message: Message):
    bot: Bot = message.bot
    birthdays = await db.get_users_birthday(14)
    text: str = await format_birthday(birthdays, 0)
    global slider
    slider = BirthdaySlider(birthdays)
    await bot.send_message(message.chat.id, text, 'MarkdownV2', reply_markup=await slider.get_slider_markup())


async def birthday_slider_callback(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    global slider
    await slider.selection(callback_query, callback_data)


async def off_birthday_notif(message: Message, state: FSMContext):
    await db.any_command("UPDATE users SET birthday_notif = false WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления отключены', reply_markup=await kb.birthday_menu(
        db.get_user_birthday_notif_on(message.from_user.id)[0]))


async def on_birthday_notif(message: Message, state: FSMContext):
    await db.any_command("UPDATE users SET birthday_notif = true WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления включены', reply_markup=await kb.birthday_menu(
        db.get_user_birthday_notif_on(message.from_user.id)[0]))


async def get_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.bot.send_message(message.from_user.id, 'Возврат в главное меню',
                                   reply_markup=await kb.event_plus_user_menu(
                                       db.get_user_event_notif_on(message.from_user.id)))


async def birthday_menu(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id, 'Укажите пункт меню',
                           reply_markup=await kb.birthday_menu(db.get_user_birthday_notif_on(message.from_user.id)[0]))


def register_user_plus_handlers(dp: Dispatcher) -> None:
    # handlers
    dp.register_message_handler(birthday_slider_start, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Показать ДР на ближайшие 14 дней')
    dp.register_message_handler(off_birthday_notif, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Отключить уведомления о ДР')
    dp.register_message_handler(on_birthday_notif, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Включить уведомления о ДР')
    dp.register_message_handler(get_menu, IsPlusUserOnly(), commands=['main_menu'])

    dp.register_message_handler(birthday_menu, IsPlusUserOrAdminOrOwner(), text='Дни рождения')

    # callbacks
    dp.register_callback_query_handler(birthday_slider_callback, IsPlusUserOrAdminOrOwner(), birthday_slider.slider_callback.filter())
