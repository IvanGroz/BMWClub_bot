import datetime

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import *
import bot.strings as st
import bot.keyboards as kb
from bot.keyboards.date_picker import date_picker_callback, DatePicker
from bot.states import RegisterUser as reg_st


async def cmd_start(message: Message):
    bot: Bot = message.bot
    await bot.send_message(message.chat.id, st.start_response, reply_markup=await kb.start_reg_message())


async def start_register(callback_query: CallbackQuery, state: FSMContext):
    bot: Bot = callback_query.bot
    await bot.answer_callback_query(callback_query.id)
    # await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.message.chat.id, st.registr_attention)
    await bot.send_message(callback_query.message.chat.id, st.input_surname)
    await state.set_state(reg_st.INSERT_SURNAME)


async def surname_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    async with state.proxy() as data:
        data['surname'] = message.text
    await bot.send_message(message.chat.id, st.input_name)
    await state.set_state(reg_st.INSERT_NAME)


async def name_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    async with state.proxy() as data:
        data['name'] = message.text
    await bot.send_message(message.chat.id, st.input_patronymic)
    await state.set_state(reg_st.INSERT_PATRONYMIC)


async def patronymic_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    async with state.proxy() as data:
        data['patronymic'] = message.text
    await bot.send_message(message.chat.id, st.input_birthday, reply_markup=await DatePicker().start_picker())
    await state.finish()


async def birthday_input(callback_query: CallbackQuery, callback_data: dict):
    date: datetime
    selected, date = await DatePicker().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'You selected {date.strftime("%d/%m/%Y")}')
        print(date)


def register_registration_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(surname_input, content_types=['text'], state=reg_st.INSERT_SURNAME)
    dp.register_message_handler(name_input, content_types=['text'], state=reg_st.INSERT_NAME)
    dp.register_message_handler(patronymic_input, content_types=['text'], state=reg_st.INSERT_PATRONYMIC)

    dp.register_callback_query_handler(start_register, lambda l: l.data == "register")
    dp.register_callback_query_handler(birthday_input, date_picker_callback.filter())
