from aiogram import Dispatcher, Bot
from aiogram.dispatcher import filters
from aiogram.types import *

from bot.filters.main import *
from bot.handlers.admin.nofitication_group import get_notification_handlers
from bot.handlers.admin.owner import get_owner_handlers
from bot.misc.formatting import format_founded_users
from bot.database import database as db

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


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(choice_new_plus_user_add, IsAdmin() or IsOwner(), IsNotificationGroupMessage(),
                                commands=['set_new_plus_user'])
    dp.register_message_handler(add_plus_user_link_callback, IsAdmin() or IsOwner(), IsNotificationGroupMessage(),
                                filters.RegexpCommandsFilter(regexp_commands=['set_new_plus_user_id([0-9]*)']))
    # other admin handlers
    get_notification_handlers(dp)
    get_owner_handlers(dp)
