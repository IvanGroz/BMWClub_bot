from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import *
import bot.strings as st
import bot.keyboards as kb
from bot.states import RegisterUser as regist


async def cmd_start(message: Message):
    bot: Bot = message.bot
    await bot.send_message(message.chat.id, st.start_response, reply_markup=await kb.start_reg_message())


async def start_register(callback_query: CallbackQuery, state: FSMContext):
    bot: Bot = callback_query.bot
    await bot.answer_callback_query(callback_query.id)
    # await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.message.chat.id, st.regist_attention)
    await bot.send_message(callback_query.message.chat.id, st.input_surname)
    await state.set_state(regist.INSERT_SURNAME)


async def surname_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    async with state.proxy() as data:
        data['surname'] = message.text
    await bot.send_message(message.chat.id, st.input_name)
    await state.set_state(regist.INSERT_NAME)


def register_registration_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(surname_input, content_types=['text'], state=regist.INSERT_SURNAME)

    dp.register_callback_query_handler(start_register, lambda l: l.data == "register")
