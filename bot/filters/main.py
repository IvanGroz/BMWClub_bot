from aiogram import Dispatcher
from aiogram.dispatcher.filters import Filter
from aiogram.types import Message, CallbackQuery

from bot.database.database import *
from bot.env import Env


class IsAdmin(Filter):
    key = "is_admin"

    async def check(self, message: Message) -> bool:
        return await is_admin(message.from_user.id)


class IsOwner(Filter):
    key = "is_owner"

    async def check(self, message: Message) -> bool:
        return await is_owner(message.from_user.id)


class IsPlusUser(Filter):
    key = "is_plus_user"

    async def check(self, message: Message) -> bool:
        return await is_plus_user(message.from_user.id)


class IsNotRegistered(Filter):
    key = "is_registered"

    async def check(self, message: Message) -> bool:
        return not (await is_registered(message.from_user.id))


class IsNotificationGroupCallback(Filter):
    key = "is_notification_group"

    async def check(self, callback: CallbackQuery) -> bool:
        if callback.message.chat.id == Env.NOTIFICATION_SUPER_GROUP_ID:
            return True
        else:
            return False


def register_all_filters(dp: Dispatcher):
    filters = (
        IsPlusUser,
        IsAdmin,
        IsOwner,
        IsNotRegistered
    )
    for filter1 in filters:
        dp.bind_filter(filter1)
