from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, Update


class LogMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0
        super(LogMiddleware, self).__init__()

    async def on_process_message(
            self,
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        self.counter += 1
        handler = current_handler.get()
        print(handler.__name__)
        #return await handler(event, data)
