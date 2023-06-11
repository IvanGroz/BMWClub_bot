import re

from aiogram import Bot
from aiogram.dispatcher import filters
from aiogram.types import *
from aiogram.utils.callback_data import CallbackData

from bot.filters.main import *
from bot.handlers.admin.nofitication_group import get_notification_handlers
from bot.handlers.admin.owner import get_owner_handlers
from bot.keyboards.simple_calendar import SimpleCalendar, simple_calendar_callback
from bot.misc.formatting import *
from bot.database import database as db
import bot.keyboards as kb
from bot.states import CreateEvent as CrEv

founded_users_dict: dict


async def choice_new_plus_user_add(message: Message, state: FSMContext):
    bot: Bot = message.bot
    users = db.find_user(message.get_args().split())
    global founded_users_dict
    founded: str = await format_founded_users(users, '/set\_new\_plus\_user\_id')
    founded_users_dict = founded[1]
    bot_mes = await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID, founded[0], ParseMode.MARKDOWN_V2)
    async with state.proxy() as data:
        data['list_users_mes'] = bot_mes


async def add_plus_user_link_callback(message: Message, state: FSMContext):
    bot: Bot = message.bot
    left, right = message.text.split('@')
    user_id = left[21:]
    db.set_new_plus_user(user_id)
    global founded_users_dict
    async with state.proxy() as data:
        list_users_mes = data['list_users_mes']
        await bot.delete_message(list_users_mes.chat.id, list_users_mes.message_id)
    await message.answer('Новый пользователь\,{}\, с расширенной функциональностью добавлен\!'.format(
        founded_users_dict.get(str(user_id))))
    await bot.delete_message(message.chat.id, message.message_id)


async def start_create_event(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await state.set_state(CrEv.INSERT_TITLE)
    await bot.send_message(message.chat.id, 'Введите название грядущего мероприятия \(заголовок\)')


async def event_title_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await state.set_state(CrEv.INSERT_DESCRIPTION)
    async with state.proxy() as data:
        data['title'] = message.text
    await bot.send_message(message.chat.id, 'Введите подробное описание того\, что будет на этом мероприятии')


async def event_description_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await state.set_state(CrEv.INSERT_LOCATION)
    async with state.proxy() as data:
        data['description'] = message.text
    await bot.send_message(message.chat.id, 'Опишите место проведения мероприятия')


async def event_location_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await state.set_state(CrEv.INSERT_DATA)
    async with state.proxy() as data:
        data['location'] = message.text
    await bot.send_message(message.chat.id, 'Выберите дату когда должно будет пройти мероприятие',
                           reply_markup=await SimpleCalendar().start_calendar())


async def event_date_input(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    bot: Bot = callback_query.bot
    date: datetime
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Вы выбрали: {date.strftime("%Y-%m-%d")}', parse_mode=ParseMode.HTML)
        async with state.proxy() as data:
            data['date'] = date
        await state.set_state(CrEv.INSERT_TIME)
        await bot.send_message(callback_query.from_user.id,
                               'Введите время начала проведения мероприятия в 24х часовом формате (Пример: 13:33)',
                               parse_mode=ParseMode.HTML)


async def event_time_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    if re.fullmatch(r'[012][0-9]:[0-5][0-9]', message.text) is not None:
        await message.answer('Время учтено\!')
        async with state.proxy() as data:
            data['time'] = message.text
        async with state.proxy() as data:
            await bot.send_message(message.chat.id,
                                   await formant_event(data['title'], data['date'], data['time'], data['location'],
                                                       data['description']), parse_mode=ParseMode.HTML)
        await bot.send_message(message.chat.id, 'Подтвердите правильность введенных данных',
                               reply_markup=await kb.end_create_event())
        await state.set_state(CrEv.FINISH_CREATE)
    else:
        await message.answer('Время введено некорректно\!')


async def correct_event(callback_query: CallbackQuery, state: FSMContext):
    await db.add_event(state)
    await callback_query.answer()
    await callback_query.message.answer('Отлично! Мероприятие создано!', parse_mode=ParseMode.HTML)
    await state.finish()


async def restart_create_event(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    await start_create_event(callback_query.message, state)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(choice_new_plus_user_add, IsAdmin(), IsNotificationGroupMessage(),
                                commands=['set_new_plus_user'])
    dp.register_message_handler(add_plus_user_link_callback, IsAdmin(), IsNotificationGroupMessage(),
                                filters.RegexpCommandsFilter(regexp_commands=['set_new_plus_user_id([0-9]*)']))
    # handlers to create an event
    dp.register_message_handler(start_create_event, IsAdmin(), text='Создать мероприятие')
    dp.register_message_handler(event_title_input, IsAdmin(), content_types=['text'], state=CrEv.INSERT_TITLE)
    dp.register_message_handler(event_description_input, IsAdmin(), content_types=['text'],
                                state=CrEv.INSERT_DESCRIPTION)
    dp.register_message_handler(event_location_input, IsAdmin(), content_types=['text'], state=CrEv.INSERT_LOCATION)

    dp.register_callback_query_handler(event_date_input, IsAdmin(), simple_calendar_callback.filter(),
                                       state=CrEv.INSERT_DATA)
    dp.register_message_handler(event_time_input, IsAdmin(), content_types=['text'], state=CrEv.INSERT_TIME)
    dp.register_callback_query_handler(correct_event, IsAdmin(), lambda l: l.data == "correct_event",
                                       state=CrEv.FINISH_CREATE)
    dp.register_callback_query_handler(restart_create_event, IsAdmin(), lambda l: l.data == "recreate_event",
                                       state=CrEv.FINISH_CREATE)
    dp.async_task()
    # other admin handlers
    get_notification_handlers(dp)
    get_owner_handlers(dp)
