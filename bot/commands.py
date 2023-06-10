from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.env import Env


async def register_all_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([BotCommand('set_plus_user',
                                             "Назначение пользователя с расширенным функционалом "
                                             "(Аргументы команды: [Фамилия] [Имя] [Отчество])")],
                                 BotCommandScopeChat(Env.NOTIFICATION_SUPER_GROUP_ID))
