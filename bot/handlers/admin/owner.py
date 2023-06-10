from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import *
import bot.keyboards as kb
from bot.env import Env
from bot.filters.main import *


async def about_input(message: Message, state: FSMContext):
    bot: Bot = message.bot
    message.get_args().split()


def get_owner_handlers(dp: Dispatcher) -> None:
    # callbacks
    dp.register_message_handler(about_input, IsOwner(), IsNotificationGroupMessage(), commands=['set_new_admin'])
