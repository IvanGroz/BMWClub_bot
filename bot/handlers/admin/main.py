from aiogram import Dispatcher

from bot.handlers.admin.nofitication_group import get_notification_handlers
from bot.handlers.admin.owner import get_owner_handlers


def register_admin_handlers(dp: Dispatcher) -> None:
    # other admin handlers
    get_notification_handlers(dp)
    get_owner_handlers(dp)
