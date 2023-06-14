from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import *
import bot.keyboards as kb
from bot.env import Env
from bot.filters.main import *
from bot.database import database as db
from bot.misc.formatting import format_founded_users
from bot.states import UpdatePermissions as UpPe

founded_users_dict: dict


async def choice_new_admin_add(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await message.answer('Введите Фамилию Имя Отчество, того человека которого хотите назначить админом '
                         '(Вводить нужно именно в указанном выше порядке в случае если не известна,'
                         ' например , фамилия, то пишите: Нет Иван Иванов и т.п.)', ParseMode.HTML)
    await state.set_state(UpPe.INSERT_ADMIN_FIO)


async def input_new_admin_fio(message: Message, state: FSMContext):
    bot: Bot = message.bot
    users = db.find_user(message.text.split())
    founded = await format_founded_users(users, "/set\_admin\_by\_id\_")
    global founded_users_dict
    founded_users_dict = founded[1]
    bot_me = await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID, founded[0], ParseMode.MARKDOWN_V2)
    await state.set_state(UpPe.CHOICE_ADMIN)
    async with state.proxy() as data:
        data['list_users_mes'] = bot_me
    if len(founded_users_dict) == 0:
        await state.finish()


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
    await state.finish()
    await bot.send_message(user_id, 'Поздравляю Вы были назначены администратором бота',
                           reply_markup=await kb.admin_menu())


async def choice_delete_admin(message: Message, state: FSMContext):
    global founded_users_dict
    bot: Bot = message.bot
    users = db.find_admins()
    founded = await format_founded_users(users, "/delete\_admin\_id")
    founded_users_dict = founded[1]
    bot_me = await bot.send_message(Env.NOTIFICATION_SUPER_GROUP_ID, founded[0], ParseMode.MARKDOWN_V2)
    async with state.proxy() as data:
        data['list_users_mes'] = bot_me
    if len(founded_users_dict) == 0:
        await state.finish()


async def delete_admin_link_callback(message: Message, state: FSMContext):
    global founded_users_dict
    bot: Bot = message.bot
    left, right = message.text.split('@')
    user_id = left[16:]
    db.delete_admin(user_id)
    async with state.proxy() as data:
        list_users_mes = data['list_users_mes']
        await bot.delete_message(list_users_mes.chat.id, list_users_mes.message_id)
    await message.answer('Админ\,{}\, удален\!'.format(founded_users_dict.get(str(user_id))))
    await bot.delete_message(message.chat.id, message.message_id)
    await state.finish()
    await bot.send_message(user_id, 'Теперь вы обычный пользователь',
                           reply_markup=await kb.regular_user_start_menu())


def get_owner_handlers(dp: Dispatcher) -> None:
    # callbacks
    dp.register_message_handler(choice_new_admin_add, IsOwnerOnly(), IsNotificationGroupMessage(),
                                commands=["set_new_admin"])
    dp.register_message_handler(input_new_admin_fio, IsOwnerOnly(), IsNotificationGroupMessage(),
                                state=UpPe.INSERT_ADMIN_FIO)
    dp.register_message_handler(add_admin_link_callback, IsOwnerOnly(), IsNotificationGroupMessage(),
                                filters.RegexpCommandsFilter(regexp_commands=['set_admin_by_id_([0-9]*)']),
                                state=UpPe.CHOICE_ADMIN)
    dp.register_message_handler(choice_delete_admin, IsOwnerOnly(), IsNotificationGroupMessage(),
                                commands=['delete_admin'])
    dp.register_message_handler(delete_admin_link_callback, IsOwnerOnly(), IsNotificationGroupMessage(),
                                filters.RegexpCommandsFilter(regexp_commands=['delete_admin_id([0-9]*)']))

