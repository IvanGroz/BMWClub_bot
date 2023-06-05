# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and setting
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils import executor
from markup import start_reg
import strings as st
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

API_TOKEN = '6210427421:AAEpZGEeuxV18QOJO18c5rYp3pxzFXK05z0'

simple_callback = CallbackData('register')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    await bot.send_message(message.chat.id, st.start_response, reply_markup=await start_reg.start_reg_message())


@dp.callback_query_handler(simple_callback.filter())
async def start_register(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    # await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.message.chat.id, st.input_name)
    await bot.send_message(callback_query.message.chat.id, st.input_name2)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
