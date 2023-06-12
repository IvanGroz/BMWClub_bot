# This is a sample Python script.
import asyncio

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and setting
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScope, BotCommandScopeChat, ParseMode
from aiogram.utils import executor

import bot.database.methods.import_in_file
from bot.commands import register_all_commands
from bot.database.methods.database_polling import start_process_db_polling
from bot.env import Env
from bot.filters import register_all_filters
from bot.handlers.main import register_all_handlers
from bot.database import database as conn


async def __on_start_up(dp: Dispatcher) -> None:
    conn.start()
    register_all_filters(dp)
    await start_process_db_polling(dp.bot)
    register_all_handlers(dp)
    await register_all_commands(dp)


def start_bot():
    bot: Bot = Bot(token=Env.TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
