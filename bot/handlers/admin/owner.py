from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import *
import bot.keyboards as kb
from bot.env import Env
from bot.filters.main import *
from bot.database import database as db
from bot.misc.formatting import format_founded_users

founded_users_dict: dict


async def choice_new_admin_add(message: Message, state: FSMContext):
    bot: Bot = message.bot
    users = db.find_user(message.get_args().split())
    founded = await format_founded_users(users, "/set\_admin\_by\_id\_")
    global founded_users_dict
    founded_users_dict = founded[1]
    bot_mes = await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID, founded[0], ParseMode.MARKDOWN_V2)
    async with state.proxy() as data:
        data['list_users_mes'] = bot_mes


async def add_admin_link_callback(message: Message, state: FSMContext):
    bot: Bot = message.bot
    left, right = message.text.split('@')
    user_id = left[17:]
    db.set_new_admin(user_id)
    global founded_users_dict
    async with state.proxy() as data:
        list_users_mes = data['list_users_mes']
        await bot.delete_message(list_users_mes.chat.id, list_users_mes.message_id)
    await message.answer('Новый админ\,{}\, добавлен\!'.format(founded_users_dict.get(str(user_id))))
    await bot.delete_message(message.chat.id, message.message_id)


def get_owner_handlers(dp: Dispatcher) -> None:
    # callbacks
    dp.register_message_handler(choice_new_admin_add, IsOwner(), IsNotificationGroupMessage(),
                                commands=['set_new_admin'])
    dp.register_message_handler(add_admin_link_callback, IsOwner(), IsNotificationGroupMessage(),
                                filters.RegexpCommandsFilter(regexp_commands=['set_admin_by_id_([0-9]*)']))
