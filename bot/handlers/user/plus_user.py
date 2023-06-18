from aiogram import Bot
from aiogram.dispatcher import filters
from aiogram.types import ParseMode

from bot.database import database as db
from bot.filters.main import *
from bot.keyboards import birthday_slider
from bot.keyboards.birthday_slider import BirthdaySlider
from bot.misc.formatting import format_birthday, format_founded_users, format_birthday_by_fio
import bot.keyboards as kb
from bot.states import AdminStates as AdSt

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


async def birthday_find_by_fio(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id,
                           'Введите ФИО пользователя, если не знаете Фамилию,'
                           ' то поиск можно вести по имени или отчеству,\n '
                           '<b>{Нет}[пробел]{Имя}</b> и <b>{Нет}[пробел]{Нет}[пробел]{Отчество}</b>, соответственно',
                           ParseMode.HTML)
    await state.set_state(AdSt.INSERT_USER_FIO_BIRTHDAY)


async def birthday_find_by_fio_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    users = db.find_user(message.text.split())
    founded = await format_founded_users(users, '/get\_birthday\_by\_id')
    founded_users_dict = founded[1]
    await state.set_state(AdSt.GET_BIRTHDAY_FIO)
    bot_me = await bot.send_message(message.from_user.id, founded[0], ParseMode.MARKDOWN_V2)

    async with state.proxy() as data:
        data['list_users_msg'] = bot_me
    if len(founded_users_dict) == 0:
        await state.finish()
    # todo выдача пользователй ДР по ФИО


async def birthday_find_link_callback(message: Message, state: FSMContext):
    bot: Bot = message.bot
    user_id = message.text[19:]
    birthday_user = await db.get_users_birthday_id(user_id)
    text = await format_birthday_by_fio(birthday_user)
    async with state.proxy() as data:
        list_users_mes = data['list_users_msg']
        await bot.delete_message(list_users_mes.chat.id, list_users_mes.message_id)
    await bot.send_message(message.chat.id, text, ParseMode.MARKDOWN_V2)
    await bot.delete_message(message.chat.id, message.message_id)


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
                                   reply_markup=await kb.plus_user_start_menu())


async def birthday_menu(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id, 'Укажите пункт меню',
                           reply_markup=await kb.birthday_menu(db.get_user_birthday_notif_on(message.from_user.id)[0]))

async def mock(message: Message, state: FSMContext):
    pass
def register_user_plus_handlers(dp: Dispatcher) -> None:
    # handlers
    dp.register_message_handler(birthday_slider_start, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Показать ДР на ближайшие 14 дней')
    dp.register_message_handler(birthday_find_by_fio, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Узнать день рождения по ФИО')
    dp.register_message_handler(off_birthday_notif, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Отключить уведомления о ДР')
    dp.register_message_handler(on_birthday_notif, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                text='Включить уведомления о ДР')
    dp.register_message_handler(birthday_find_by_fio_input, IsPlusUserOrAdminOrOwner(), content_types=['text'],
                                state=AdSt.INSERT_USER_FIO_BIRTHDAY)
    dp.register_message_handler(birthday_find_link_callback, IsAdminOrOwner(),
                                filters.RegexpCommandsFilter(regexp_commands=['get_birthday_by_id([0-9]*)']),
                                state=AdSt.GET_BIRTHDAY_FIO)
    dp.register_message_handler(mock, IsPlusUserOnly(), commands=['main_menu'])

    dp.register_message_handler(birthday_menu, IsPlusUserOrAdminOrOwner(), text='Дни рождения')

    # callbacks
    dp.register_callback_query_handler(birthday_slider_callback, IsPlusUserOrAdminOrOwner(),
                                       birthday_slider.slider_callback.filter())
