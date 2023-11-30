from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, Update
from bot.filters.main import *
from bot.handlers.user import main as regular_user
from bot.handlers.user import plus_user
from bot.handlers.admin import main as adm
from bot.handlers.registration import main as registr


class LogMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0
        super(LogMiddleware, self).__init__()

    async def on_process_message(
            self,
            message: Message,
            data: Dict[str, Any]
    ) -> Any:
        self.counter += 1
        state = data.get("state")
        handler = current_handler.get()
        if message.text == '/main_menu':
            if await IsAdminOrOwner().check(message):
                await adm.get_menu(message=message, state=state)
            if await IsRegularUserOnly().check(message):
                await regular_user.get_menu(message=message, state=state)
            if await IsPlusUserOnly().check(message):
                await plus_user.get_menu(message=message, state=state)
            if await IsNotRegistered().check(message):
                await registr.get_menu(message)
            raise CancelHandler()

        print(handler.__name__)
        # return await handler(event, data)
