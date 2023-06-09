from aiogram import Dispatcher

from bot.handlers.admin.nofitication_group import get_notification_handlers


def register_admin_handlers(dp: Dispatcher) -> None:
    # other admin handlers
    get_notification_handlers(dp)
