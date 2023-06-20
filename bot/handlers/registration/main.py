import asyncio
import datetime
import re

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

import bot.keyboards as kb
import bot.res.strings as st
from bot.database import database as conn
from bot.env import Env
from bot.filters.main import IsNotRegistered
from bot.keyboards.date_picker import date_picker_callback, DatePicker
from bot.misc.formatting import replace_markdown_marks
from bot.res.states import RegisterUser as RegState


async def cmd_start(message: Message):
    bot: Bot = message.bot
    await bot.send_message(message.chat.id, st.start_response, reply_markup=await kb.start_reg_message())


async def get_menu(message: Message, state: FSMContext):
    await message.bot.send_message(message.from_user.id, 'Меню открыто', reply_markup=await kb.registration_menu())


async def start_register(callback_query: CallbackQuery, state: FSMContext):
    bot: Bot = callback_query.bot
    if callback_query.data == 'register_partner':
        await bot.send_message(callback_query.message.chat.id, st.registr_attention_partner)
        async with state.proxy() as data:
            data['is_business'] = 'partner'
    if callback_query.data == 'register_ads':
        await bot.send_message(callback_query.message.chat.id, st.registr_attention_ads)
        async with state.proxy() as data:
            data['is_business'] = 'ads'
    if callback_query.data == 'register':
        await bot.send_message(callback_query.message.chat.id, st.registr_attention)

    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['user_id'] = callback_query.from_user.id
    # await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.message.chat.id, st.input_surname, reply_markup=await kb.registration_menu())
    await state.set_state(RegState.INSERT_SURNAME)


async def permanent_menu(message: Message, state: FSMContext) -> bool:
    bot: Bot = message.bot
    if message.text == 'Допустил ошибку/Начать заново':
        await cmd_start(message)
        await state.finish()
        return True
    if message.text == 'Получить помощь по регистрации':
        await bot.send_message(message.chat.id, st.registration_help)
        await state.set_state(RegState.HELP_QUESTION)
        return True


async def help_question_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    if message.text != 'Получить помощь по регистрации' and message.text != 'Допустил ошибку/Начать заново':
        await bot.send_message(message.chat.id, st.registration_help_answer)
        msg = await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID, message.text,
                                     message_thread_id=Env.QUESTION_THREAD_ID,
                                     reply_markup=await kb.question_answer(message.from_user.id))
        await state.finish()
        await asyncio.sleep(169200)  # 47 часов спустя удалять обращение
        await bot.delete_message(chat_id=Env.NOTIFICATION_SUPER_GROUP_ID, message_id=msg.message_id)


async def surname_input(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        if await permanent_menu(message, state):
            return
        bot: Bot = message.bot
        async with state.proxy() as data:
            data['surname'] = message.text
        await bot.send_message(message.chat.id, st.input_name)
        await state.set_state(RegState.INSERT_NAME)


async def name_input(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        if await permanent_menu(message, state):
            return
        bot: Bot = message.bot
        async with state.proxy() as data:
            data['name'] = message.text
        await bot.send_message(message.chat.id, st.input_patronymic)
        await state.set_state(RegState.INSERT_PATRONYMIC)


async def patronymic_input(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        if await permanent_menu(message, state):
            return
        bot: Bot = message.bot
        async with state.proxy() as data:
            data['patronymic'] = message.text
            business_type: str = ''
            try:
                business_type = data['is_business']
            except KeyError:
                pass

        if business_type == 'partner' or business_type == 'ads':
            await state.set_state(RegState.INSERT_ABOUT_BUSINESS)
            if business_type == 'partner':
                await bot.send_message(message.chat.id, st.about_partner_info)
            else:
                await bot.send_message(message.chat.id, st.about_ads_info)
        else:
            await bot.send_message(message.chat.id, st.input_birthday, reply_markup=await DatePicker().start_picker())
            await state.set_state(RegState.NEUTRAL)


async def info_about_business(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        bot: Bot = message.bot
        async with state.proxy() as data:
            business_type: str = ''
            try:
                business_type = data['is_business']
            except KeyError:
                pass
            if business_type == 'partner':
                await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID,
                                       '[{} {} {}](tg://user?id={}) хочет стать партнером\!\n'
                                       'В качестве данных о себе как о партнёре указал:\n{}'.format(
                                           data['surname'], data['name'], data['patronymic'], data['user_id'],
                                           await replace_markdown_marks(message.text)),
                                       ParseMode.MARKDOWN_V2, message_thread_id=Env.NEW_PARTNER_THREAD_ID)
            if business_type == 'ads':
                await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID,
                                       '[{} {} {}](tg://user?id={}) хотел бы сотрудничать как рекламодатель\n'
                                       'В качестве данных о себе как об организации указал:\n*{}*'.format(
                                           data['surname'], data['name'], data['patronymic'], data['user_id'],
                                           await replace_markdown_marks(message.text)),
                                       ParseMode.MARKDOWN_V2, message_thread_id=Env.NEW_ADS_THREAD_ID)
        await bot.send_message(message.from_user.id, st.business_info_answer)
        await state.finish()


async def birthday_input(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    if await permanent_menu(callback_query.message, state):
        return
    date: datetime
    selected, date = await DatePicker().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Вы выбрали: {date.strftime("%Y-%m-%d")}')
        async with state.proxy() as data:
            data['birthday'] = date
        await state.set_state(RegState.INSERT_ABOUT)
        await callback_query.bot.send_message(callback_query.from_user.id, st.input_about)


async def about_input(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        if await permanent_menu(message, state):
            return
        bot: Bot = message.bot
        async with state.proxy() as data:
            data['about'] = message.text
        await state.set_state(RegState.INSERT_CAR_PHOTO)
        await bot.send_message(message.chat.id, st.input_car_photo)


async def car_photo_input(message: Message, state: FSMContext):
    if await permanent_menu(message, state):
        return
    bot: Bot = message.bot
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id  # Т.к. все файлы хранятся в телеграме, то найти их можно по file_id
    await message.answer('Фото загружено!')
    await bot.send_photo(message.chat.id, photo=InputFile('bot//res//number_plate.png'),
                         caption=st.input_car_number_plate, reply_markup=await kb.car_number_plate_non_rus())
    await state.set_state(RegState.INSERT_NUMBER_PLATE)


async def number_plate_input(message: Message, state: FSMContext):
    if await permanent_menu(message, state):
        return
    bot: Bot = message.bot
    if (re.fullmatch(r'[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}-\d{2,3}', message.text) is not None) or (
            re.fullmatch(r'[ABEKMHOPCTYX]\d{3}[ABEKMHOPCTYX]{2}-\d{2,3}', message.text) is not None):
        async with state.proxy() as data:
            data['number_plate'] = message.text
        await state.set_state(RegState.NEUTRAL)
        await bot.send_message(message.chat.id, st.input_phone_number, reply_markup=await kb.get_phone_number())
    else:
        await message.answer(st.err_input_number_plate)


async def non_russian_plate(callback_query: CallbackQuery, state: FSMContext):
    if await permanent_menu(callback_query.message, state):
        return
    bot: Bot = callback_query.bot
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(RegState.INSERT_NON_RUS_PLATE)
    await bot.send_message(callback_query.from_user.id, st.input_non_rus_car_number_plate)


async def non_russian_plate_input(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        if await permanent_menu(message, state):
            return
        bot: Bot = message.bot
        async with state.proxy() as data:
            data['number_plate'] = message.text
        await state.set_state(RegState.NEUTRAL)
        await bot.send_message(message.chat.id, st.input_phone_number, reply_markup=await kb.get_phone_number())


async def phone_number_input(message: Message, state: FSMContext):
    if await permanent_menu(message, state):
        return
    bot: Bot = message.bot
    if message.contact is not None:
        async with state.proxy() as data:
            data['phone_number'] = message.contact.phone_number
        await bot.send_message(message.chat.id, 'Ваш номер телефона записан!',
                               reply_markup=await kb.registration_menu())
        await bot.send_message(message.chat.id, st.partner_choice, reply_markup=await kb.partner_choice())


async def wanna_be_partner(callback_query: CallbackQuery, state: FSMContext):
    if await permanent_menu(callback_query.message, state):
        return
    bot: Bot = callback_query.bot
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(RegState.INSERT_PARTNER_BUSINESS)
    await bot.send_message(callback_query.from_user.id, st.about_partner_info)


async def wanna_be_partner_input(message: Message, state: FSMContext):
    if not message.text.startswith('/'):
        if await permanent_menu(message, state):
            return
        bot: Bot = message.bot
        async with state.proxy() as data:
            data['partner'] = message.text
            await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID,
                                   'Новый участник хочет стать партнером\!\n Это [{} {} {}](tg://user?id={})\n'
                                   'В качестве данных о себе как о партнёре указал:\n{}'.format(
                                       data['surname'], data['name'], data['patronymic'], data['user_id'],
                                       await replace_markdown_marks(message.text)),
                                   'MarkdownV2',
                                   message_thread_id=Env.NEW_PARTNER_THREAD_ID)
        await state.set_state(RegState.NEUTRAL)
        await bot.send_message(message.chat.id, st.end_registration, reply_markup=await kb.end_registration())


async def no_partner(callback_query: CallbackQuery, state: FSMContext):
    if await permanent_menu(callback_query.message, state):
        return
    bot: Bot = callback_query.bot
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['partner'] = 'Нет'
    await state.set_state(RegState.NEUTRAL)
    await bot.send_message(callback_query.from_user.id, st.end_registration, reply_markup=await kb.end_registration())


async def end_registration(callback_query: CallbackQuery, state: FSMContext):
    bot: Bot = callback_query.bot
    await bot.answer_callback_query(callback_query.id)
    await conn.add_user(state)
    async with state.proxy() as data:
        await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID,
                               "Новый участник\! Это [{} {} {}](tg://user?id={})".format(
                                   data['surname'],
                                   data['name'],
                                   data['patronymic'],
                                   data['user_id']),
                               ParseMode.MARKDOWN_V2, message_thread_id=Env.NEW_MEMBER_THREAD_ID)
    await state.finish()
    await bot.send_message(callback_query.from_user.id, st.finish_registration,
                           reply_markup=await kb.regular_user_start_menu())


async def mock(message: Message, state: FSMContext):
    pass


def register_registration_handlers(dp: Dispatcher) -> None:
    # message handlers
    dp.register_message_handler(cmd_start, IsNotRegistered(), CommandStart())
    dp.register_message_handler(surname_input, IsNotRegistered(), content_types=['text'], state=RegState.INSERT_SURNAME)
    dp.register_message_handler(name_input, IsNotRegistered(), content_types=['text'], state=RegState.INSERT_NAME)
    dp.register_message_handler(patronymic_input, IsNotRegistered(), content_types=['text'],
                                state=RegState.INSERT_PATRONYMIC)
    dp.register_message_handler(about_input, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.INSERT_ABOUT)
    dp.register_message_handler(car_photo_input, IsNotRegistered(), content_types=[ContentType.PHOTO],
                                state=RegState.INSERT_CAR_PHOTO)
    dp.register_message_handler(number_plate_input, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.INSERT_NUMBER_PLATE)
    dp.register_message_handler(non_russian_plate_input, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.INSERT_NON_RUS_PLATE)
    dp.register_message_handler(phone_number_input, IsNotRegistered(), content_types=[ContentType.CONTACT],
                                state=RegState.NEUTRAL)
    dp.register_message_handler(wanna_be_partner_input, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.INSERT_PARTNER_BUSINESS)
    dp.register_message_handler(help_question_input, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.HELP_QUESTION)
    dp.register_message_handler(info_about_business, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.INSERT_ABOUT_BUSINESS)
    dp.register_message_handler(mock, IsNotRegistered(), commands=['main_menu'])
    dp.register_message_handler(permanent_menu, IsNotRegistered(), content_types=[ContentType.TEXT],
                                state=RegState.NEUTRAL)
    # callbacks
    dp.register_callback_query_handler(non_russian_plate, IsNotRegistered(), lambda l: l.data == "non_rus_plate",
                                       state=RegState.INSERT_NUMBER_PLATE)

    dp.register_callback_query_handler(start_register, IsNotRegistered(),
                                       lambda l: l.data == "register" or
                                                 l.data == "register_partner"
                                                 or l.data == "register_ads")
    dp.register_callback_query_handler(birthday_input, IsNotRegistered(), date_picker_callback.filter(),
                                       state=RegState.NEUTRAL)
    dp.register_callback_query_handler(wanna_be_partner, IsNotRegistered(), lambda l: l.data == "wanna_be_partner",
                                       state=RegState.NEUTRAL)
    dp.register_callback_query_handler(no_partner, IsNotRegistered(), lambda l: l.data == "no_partner",
                                       state=RegState.NEUTRAL)
    dp.register_callback_query_handler(end_registration, IsNotRegistered(), lambda l: l.data == "end_registration",
                                       state=RegState.NEUTRAL)
