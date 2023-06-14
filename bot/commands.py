from aiogram import Dispatcher
from aiogram.types import *

from bot.env import Env


async def register_all_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [BotCommand('set_new_plus_user', "Назначение пользователя с расширенным функционалом "),
         BotCommand('set_new_admin', "Назначение пользователя админом "),
         BotCommand('delete_plus_user', "Удаление пользователя с расширенным функционалом "),
         BotCommand('delete_admin', "Удаление админа ")
         ],
        BotCommandScopeChat(Env.NOTIFICATION_SUPER_GROUP_ID))
    await dp.bot.set_my_commands([BotCommand('main_menu', "Возврат в главное меню")],
                                 BotCommandScopeAllPrivateChats())
