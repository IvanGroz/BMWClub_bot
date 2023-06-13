from aiogram import Dispatcher
from aiogram.dispatcher.filters import Filter
from aiogram.types import Message, CallbackQuery

from bot.database.database import *
from bot.env import Env


class IsAdminOrOwner(Filter):
    key = "is_admin"

    async def check(self, message: Message) -> bool:
        return await is_admin(message.from_user.id) or await is_owner(message.from_user.id)


class IsOwnerOnly(Filter):
    key = "is_owner"

    async def check(self, message: Message) -> bool:
        return await is_owner(message.from_user.id)


class IsPlusUserOrAdminOrOwner(Filter):
    key = "is_plus_user"

    async def check(self, message: Message) -> bool:
        return await is_plus_user(message.from_user.id) or await is_admin(message.from_user.id) or await is_owner(
            message.from_user.id)


class IsPlusUserOnly(Filter):
    key = "is_plus_user_only"

    async def check(self, message: Message) -> bool:
        return await is_plus_user(message.from_user.id) and not await is_admin(
            message.from_user.id) and not await is_owner(
            message.from_user.id)


class IsNotRegistered(Filter):
    key = "is_not_registered"

    async def check(self, message: Message) -> bool:
        return not (await is_registered(message.from_user.id))


class IsRegularUserOrPlusUser(Filter):
    key = "is_regular_user_and_plus"

    async def check(self, message: Message) -> bool:
        return await IsRegularUserOnly().check(message) or await IsPlusUserOnly().check(message)


class IsRegistered(Filter):
    key = "is_regular_user"

    async def check(self, message: Message) -> bool:
        return await is_registered(message.from_user.id)


class IsRegularUserOnly(Filter):
    key = "is_regular_user_only"

    async def check(self, message: Message) -> bool:
        return (not (await is_plus_user(message.from_user.id)
                     or await is_admin(message.from_user.id)
                     or await is_owner(message.from_user.id)))


class IsNotificationGroupCallback(Filter):
    key = "is_notification_group"

    async def check(self, callback: CallbackQuery) -> bool:
        if callback.message.chat.id == Env.NOTIFICATION_SUPER_GROUP_ID:
            return True
        else:
            return False


class IsNotificationGroupMessage(Filter):
    key = "is_notification_group_msg"

    async def check(self, msg: Message) -> bool:
        if msg.chat.id == Env.NOTIFICATION_SUPER_GROUP_ID:
            return True
        else:
            return False


def register_all_filters(dp: Dispatcher):
    filters = (
        IsAdminOrOwner,
        IsOwnerOnly,
        IsPlusUserOrAdminOrOwner,
        IsPlusUserOnly,
        IsNotRegistered,
        IsRegularUserOrPlusUser,
        IsRegistered,
        IsRegularUserOnly,
        IsNotificationGroupCallback,
        IsNotificationGroupMessage

    )
    for filter1 in filters:
        dp.bind_filter(filter1)
