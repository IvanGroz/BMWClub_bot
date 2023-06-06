from aiogram import Dispatcher

from bot.handlers.user.main import register_user_handlers
from bot.handlers.registration import register_registration_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_user_handlers,
        register_registration_handlers,
        # todo:
        # register_admin_handlers,
        # register_other_handlers,
    )
    for handler in handlers:
        handler(dp)
