import calendar
import re

from aiogram import Bot
from aiogram.dispatcher import filters
from aiogram.types import *
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import ChatNotFound

from bot.database.methods.import_in_file import get_all_users_info
from bot.filters.main import *
from bot.handlers.admin.nofitication_group import get_notification_handlers
from bot.handlers.admin.owner import get_owner_handlers
from bot.keyboards.events_slider_admin import EventsSliderAdmin, event_slider_admin_callback
from bot.keyboards.simple_calendar import SimpleCalendar, simple_calendar_callback
from bot.misc.anti_swearing import is_swearing
from bot.misc.formatting import *
from bot.database import database as db
import bot.keyboards as kb
from bot.states import CreateEvent as CrEv
from bot.states import EditEvent as EdEv
from bot.states import UpdatePermissions as UpPe
from bot.states import AdminStates as AdSt

founded_users_dict: dict


async def choice_new_plus_user_add(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await message.answer('Введите Фамилию Имя Отчество, того человека которого хотите назначить админом '
                         '(Вводить нужно именно в указанном выше порядке в случае если не известна,'
                         ' например , фамилия, то пишите: Нет Иван Иванов и т.п.)', ParseMode.HTML)
    await state.set_state(UpPe.INSERT_USER_PLUS_FIO)


async def input_new_user_plus_fio(message: Message, state: FSMContext):
    bot: Bot = message.bot
    users = db.find_user(message.text.split())
    global founded_users_dict
    founded: str = await format_founded_users(users, '/set\_new\_plus\_user\_id')
    founded_users_dict = founded[1]
    bot_me = await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID, founded[0], ParseMode.MARKDOWN_V2)
    await state.set_state(UpPe.CHOICE_USER_PLUS)
    async with state.proxy() as data:
        data['list_users_mes'] = bot_me
    if len(founded_users_dict) == 0:
        await state.finish()


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
                                   await format_event(data['title'], data['date'], data['time'], data['location'],
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
    await callback_query.answer()
    await start_create_event(callback_query.message, state)


event_slider: EventsSliderAdmin


async def watch_events(message: Message, state: FSMContext):
    bot: Bot = message.bot
    list_event = await db.get_list_event()
    global event_slider
    event_slider = EventsSliderAdmin(list_event)
    await bot.send_message(message.chat.id,
                           await format_event_extended(list_event[0][1], list_event[0][2], list_event[0][3],
                                                       list_event[0][4], list_event[0][5], list_event[0][6]),
                           ParseMode.HTML,
                           reply_markup=await event_slider.get_slider_markup()
                           )


async def event_slider_callback(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    global event_slider
    edit, event_id = await event_slider.selection(callback_query, callback_data)
    await callback_query.answer()
    if edit:
        await callback_query.bot.send_message(callback_query.from_user.id, 'Что нужно отредактировать?',
                                              reply_markup=await kb.edit_event())
        async with state.proxy() as data:
            data['edit_event_id'] = event_id


async def event_edit_location(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.bot.send_message(callback_query.from_user.id, 'Введите новую локацию')
    await state.set_state(EdEv.INSERT_LOCATION)


async def edit_event_input_location(message: Message, state: FSMContext):
    bot: Bot = message.bot
    async with state.proxy() as data:
        db.edit_event(data['edit_event_id'], message.text)
        await bot.send_message(message.chat.id, 'Локация изменена')
    await state.finish()


async def event_edit_date_time(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.bot.send_message(callback_query.from_user.id,
                                          'Введите дату и время, в формате: 2023-05-24/13:45', ParseMode.HTML)
    await state.set_state(EdEv.INSERT_DATA_TIME)


async def edit_event_input_date_time(message: Message, state: FSMContext):
    bot: Bot = message.bot
    try:
        date, time = message.text.split('/')
        if re.fullmatch(r'[012][0-9]:[0-5][0-9]', time) is not None:
            try:
                datetime.date.fromisoformat(date)
                async with state.proxy() as data:
                    db.edit_event(data['edit_event_id'], date=date, time=time)
                    await bot.send_message(message.chat.id, 'Дата/время изменены')
                await state.finish()
            except ValueError:
                await bot.send_message(message.chat.id, 'Неправильно введена дата формат: YYYY-MM-DD', ParseMode.HTML)
        else:
            await bot.send_message(message.chat.id, 'Неправильно введено время формат: hh:mm')
    except ValueError:
        await bot.send_message(message.chat.id, 'Неправильно введены данные')


async def event_edit_title_desc(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.bot.send_message(callback_query.from_user.id,
                                          'Введите название мероприятия и его описание, в формате: Название/Описание')
    await state.set_state(EdEv.INSERT_TITLE_DESCRIPTION)


async def edit_event_input_title_desc(message: Message, state: FSMContext):
    bot: Bot = message.bot
    try:
        title, description = message.text.split('/')
        async with state.proxy() as data:
            db.edit_event(data['edit_event_id'], title=title, description=description)
            await bot.send_message(message.chat.id, 'Название и описание мероприятия изменены')
        await state.finish()
    except ValueError:
        await bot.send_message(message.chat.id, 'Данные введены некорректно')


async def event_delete(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    async with state.proxy() as data:
        db.delete_event(data['edit_event_id'])
        await callback_query.bot.send_message(callback_query.from_user.id, 'Событие удалено!', ParseMode.HTML)
    await state.finish()


async def event_cancel_edit(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    await state.finish()


async def get_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.bot.send_message(message.from_user.id, 'Возврат в главное меню', reply_markup=await kb.admin_menu())


async def birthday_menu(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id, 'Укажите пункт меню',
                           reply_markup=await kb.birthday_menu(db.get_user_birthday_notif_on(message.from_user.id)[0]))


async def event_menu(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id, 'Укажите пункт меню',
                           reply_markup=await kb.event_admin_menu(db.get_user_event_notif_on(message.from_user.id)[0]))


async def off_events_notif(message: Message, state: FSMContext):
    await db.any_command("UPDATE users SET event_notif = false WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления отключены', reply_markup=await kb.event_admin_menu(
        db.get_user_event_notif_on(message.from_user.id)[0]))


async def on_events_notif(message: Message, state: FSMContext):
    await db.any_command("UPDATE users SET event_notif = true WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления включены', reply_markup=await kb.event_admin_menu(
        db.get_user_event_notif_on(message.from_user.id)[0]))


async def broadcast(message: Message, state: FSMContext):
    await message.answer('Напишите сообщение, которое будет доставлено всем авторизованным пользователям в лс от бота')
    await state.set_state(AdSt.INSERT_BROADCAST)


async def broadcast_input(message: Message, state: FSMContext):
    if not await is_swearing(message.text):
        await message.answer('Сообщение принято')
        await state.finish()
        user_ids = await db.any_command("SELECT user_id from users")
        for user_id in user_ids:
            try:
                await message.bot.send_message(user_id[0], "<b>Важное объявление!</b>\n" + message.text, ParseMode.HTML)
            except ChatNotFound:
                pass
    else:
        await message.answer('Такие сообщения не допускаются к публикации!', ParseMode.HTML)


async def users_info_menu(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id, "Выберите пункт меню", reply_markup=await kb.users_info_menu())


async def user_info_by_fio(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id,
                           'Введите ФИО пользователя, если не знаете Фамилию,'
                           ' то поиск можно вести по имени или отчеству, '
                           '<b>Нет Имя</b> и <b>Нет Нет Фамилия</b>, соответственно',
                           ParseMode.HTML)
    if message.text == 'Редактировать пользователя':
        await state.set_state(AdSt.EDIT_USER)
    if message.text == "Найти пользователя по ФИО":
        await state.set_state(AdSt.INSERT_USER_FIO)


async def user_info_by_fio_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    users = db.find_user(message.text.split())
    global founded_users_dict
    # sm = await state.get_state()
    if await state.get_state() == 'AdminStates:EDIT_USER':
        founded = await format_founded_users(users, '/edit\_user\_info\_id')
        founded_users_dict = founded[1]
        await state.set_state(AdSt.CHOICE_USER_EDIT)
    if await state.get_state() == 'AdminStates:INSERT_USER_FIO':
        founded = await format_founded_users(users, '/get\_user\_info\_id')
        founded_users_dict = founded[1]
        await state.set_state(AdSt.CHOICE_USER_INFO)
    bot_me = await bot.send_message(message.from_user.id, founded[0], ParseMode.MARKDOWN_V2)

    async with state.proxy() as data:
        data['list_users_msg'] = bot_me
    if len(founded_users_dict) == 0:
        await state.finish()


async def edit_user_info_by_fio_link_choice(message: Message, state: FSMContext):
    bot: Bot = message.bot
    user_id = message.text[18:]
    user = await db.get_user_by_id(user_id)
    async with state.proxy() as data:
        list_users_mes = data['list_users_msg']
        await bot.delete_message(list_users_mes.chat.id, list_users_mes.message_id)
        data['edit_user_id'] = user_id
    text, file_id = await user_info(user)
    await bot.send_photo(message.from_user.id, file_id, text,
                         parse_mode=ParseMode.HTML)  # Тут описание найденного пользователя
    await bot.send_message(message.chat.id, "Выберите поле которое хотите отредактировать\n"
                                            "1.Дата рождения\n"
                                            "2.Номер телефона\n"
                                            "3.Род деятельности\n"
                                            "4.Информация о партнерстве\n"
                                            "5.Гос.номер\n\n "
                                            "Отправьте:{номер}[пробел]{значение поля} \n\n"
                                            "Если Вы хотите изменить фото авто, просто отправьте фото"
                           , parse_mode=ParseMode.HTML)
    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state(AdSt.EDIT_DATA_USER)


async def edit_user_data(message: Message, state: FSMContext):
    bot: Bot = message.bot
    user_id: int
    async with state.proxy() as data:
        user_id = int(data['edit_user_id'])
    if len(message.photo) != 0:
        await state.finish()
        await db.any_command("UPDATE car SET car_photo_file_id = '{}'"
                             " WHERE id = (select car_id from users where user_id={})".format(message.photo[0].file_id,
                                                                                              user_id))
        await message.answer('Фото машины изменено')
    else:
        if re.fullmatch(r'[1-5] .*', message.text) is not None:
            left, right = message.text.split()
            match left:
                case '1':  # Дата рождения
                    try:
                        datetime.date.fromisoformat(right)
                        await db.any_command(
                            "UPDATE users SET birthday = '{}' WHERE user_id = {}".format(right, user_id))
                        await message.answer('Дата рождения изменена')

                    except ValueError:
                        await bot.send_message(message.chat.id, 'Неправильно введена дата формат: YYYY-MM-DD',
                                               ParseMode.HTML)
                case '2':  # Номер телефона
                    await db.any_command(
                        "UPDATE users SET phone_number = '{}' WHERE user_id = {}".format(right, user_id))
                    await message.answer('Номер телефона изменен')

                case '3':  # Род деятельности
                    await db.any_command("UPDATE users SET about = '{}' WHERE user_id = {}".format(right, user_id))
                    await message.answer('Род деятельности исправлен')

                case '4':  # Информация о партнерстве
                    await db.any_command("UPDATE users SET partner = '{}' WHERE user_id = {}".format(right, user_id))
                    await message.answer('Информация о партнерстве исправлена')

                case '5':  # Гос.номер
                    await db.any_command("UPDATE car SET number_plate = '{}'"
                                         " WHERE id = "
                                         "(select car_id from users where user_id={})".format(right, user_id))
                    await message.answer('Гос.номер исправлен')
                    pass
            await state.finish()
        else:
            await message.answer('Должна быть только одна из цифр выше')


async def user_info_by_fio_link_choice(message: Message, state: FSMContext):
    bot: Bot = message.bot
    user_id = message.text[17:]
    user = await db.get_user_by_id(user_id)
    async with state.proxy() as data:
        list_users_mes = data['list_users_msg']
        await bot.delete_message(list_users_mes.chat.id, list_users_mes.message_id)
    text, file_id = await user_info(user)
    await bot.send_photo(message.from_user.id, file_id, text, parse_mode=ParseMode.HTML)
    await bot.delete_message(message.chat.id, message.message_id)
    await state.finish()


async def all_users_info(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await get_all_users_info()
    await bot.send_document(message.chat.id, open(r'users_data.csv', 'rb'),
                            caption='В данном файле содержится вся нужная информация о пользователях,'
                                    ' открывать ее нужно на ПК с помощью Exel'
                                    'для того чтобы привести данные в надлежащий вид:\n'
                                    '1.Выделяем всю первую колонку\n\n'
                                    '2.В разделе "Данные" выбираем "Текст по столбцам"\n\n'
                                    '3.В диалоговом окне "Укажите формат данных" выберите '
                                    '"С разделителями" и нажмите "Далее"\n\n'
                                    '4.Символом-разделителем является: Ставьте галочку на "запятая"\n\n'
                                    '5.Нажимаем "Готово"\n', parse_mode=ParseMode.HTML)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(choice_new_plus_user_add, IsAdmin(), IsNotificationGroupMessage(),
                                commands=['set_new_plus_user'])
    dp.register_message_handler(add_plus_user_link_callback, IsAdmin(), IsNotificationGroupMessage(),
                                filters.RegexpCommandsFilter(regexp_commands=['set_new_plus_user_id([0-9]*)']),
                                state=UpPe.CHOICE_USER_PLUS)
    dp.register_message_handler(input_new_user_plus_fio, IsAdmin(), IsNotificationGroupMessage(),
                                state=UpPe.INSERT_USER_PLUS_FIO)
    dp.register_message_handler(broadcast_input, IsAdmin(), state=AdSt.INSERT_BROADCAST)
    dp.register_message_handler(user_info_by_fio_input, IsAdmin(), state=AdSt.EDIT_USER)
    dp.register_message_handler(edit_user_data, IsAdmin(), state=AdSt.EDIT_DATA_USER, content_types=['text', 'photo'])
    dp.register_message_handler(user_info_by_fio_input, IsAdmin(), state=AdSt.INSERT_USER_FIO)
    dp.register_message_handler(user_info_by_fio_link_choice, IsAdmin(),
                                filters.RegexpCommandsFilter(regexp_commands=['get_user_info_id([0-9]*)']),
                                state=AdSt.CHOICE_USER_INFO)
    dp.register_message_handler(edit_user_info_by_fio_link_choice, IsAdmin(),
                                filters.RegexpCommandsFilter(regexp_commands=['edit_user_info_id([0-9]*)']),
                                state=AdSt.CHOICE_USER_EDIT)
    dp.register_message_handler(get_menu, IsAdmin(), commands=['main_menu'])
    # handlers to create an event
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

    dp.register_callback_query_handler(event_slider_callback, IsAdmin(), event_slider_admin_callback.filter())

    # edit events handlers
    dp.register_callback_query_handler(event_edit_location, IsAdmin(), lambda l: l.data == "location_edit")
    dp.register_message_handler(edit_event_input_location, IsAdmin(), content_types=['text'],
                                state=EdEv.INSERT_LOCATION)
    dp.register_callback_query_handler(event_edit_date_time, IsAdmin(), lambda l: l.data == "data/time_edit")
    dp.register_message_handler(edit_event_input_date_time, IsAdmin(), content_types=['text'],
                                state=EdEv.INSERT_DATA_TIME)
    dp.register_callback_query_handler(event_edit_title_desc, IsAdmin(), lambda l: l.data == "title_and_desc_edit")
    dp.register_message_handler(edit_event_input_title_desc, IsAdmin(), content_types=['text'],
                                state=EdEv.INSERT_TITLE_DESCRIPTION)
    dp.register_callback_query_handler(event_delete, IsAdmin(), lambda l: l.data == "delete_event")
    dp.register_callback_query_handler(event_cancel_edit, IsAdmin(), lambda l: l.data == "cancel_event")

    # основное меню
    dp.register_message_handler(birthday_menu, IsAdmin(), text='Дни рождения')
    dp.register_message_handler(broadcast, IsAdmin(), text='Рассылка')
    dp.register_message_handler(event_menu, IsAdmin(), text='Мероприятия клуба')
    dp.register_message_handler(users_info_menu, IsAdmin(), text='Информация о пользователях')
    dp.register_message_handler(user_info_by_fio, IsAdmin(), content_types=['text'], text='Редактировать пользователя')

    # подпункты меню
    dp.register_message_handler(watch_events, IsAdmin(), text='Ближайшие мероприятия')
    dp.register_message_handler(start_create_event, IsAdmin(), text='Создать мероприятие')
    dp.register_message_handler(off_events_notif, IsAdmin(), content_types=['text'], text='Отключить уведомления')
    dp.register_message_handler(on_events_notif, IsAdmin(), content_types=['text'], text='Включить уведомления')
    dp.register_message_handler(user_info_by_fio, IsAdmin(), content_types=['text'], text='Найти пользователя по ФИО')
    dp.register_message_handler(all_users_info, IsAdmin(), content_types=['text'],
                                text='Получить данные о всех пользователях')

    # Для Др подпункты такие же как и для user plus, реализация в: bot/handlers/user/plus_user.py
    # other admin handlers
    get_notification_handlers(dp)
    get_owner_handlers(dp)
