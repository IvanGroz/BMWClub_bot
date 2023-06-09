# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and setting
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from bot.database.methods.birthday_polling import start_process_db_polling
from bot.env import Env
from bot.filters import register_all_filters
from bot.handlers.main import register_all_handlers
from bot.database import database as conn


async def __on_start_up(dp: Dispatcher) -> None:
    conn.start()
    register_all_filters(dp)
    register_all_handlers(dp)
    await start_process_db_polling(dp.bot)


def start_bot():
    bot: Bot = Bot(token=Env.TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
