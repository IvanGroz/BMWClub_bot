from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils import executor

from bot.commands import register_all_commands
from bot.database import database as conn
from bot.database.methods.database_polling import start_process_db_polling
from bot.handlers.main import register_all_handlers
from bot.misc.log_middleware import *


async def __on_start_up(dp: Dispatcher) -> None:
    conn.start()
    register_all_filters(dp)
    await register_all_commands(dp)
    register_all_handlers(dp)
    await start_process_db_polling(dp.bot)


def start_bot():
    bot: Bot = Bot(token=Env.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.setup_middleware(LogMiddleware())

    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
