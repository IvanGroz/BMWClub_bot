import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from bot.misc.formatting import *

event_slider_callback_data = CallbackData('slider_event', 'action_event_user', 'index_event')


class EventsSlider:
    def __init__(self, events):
        self.events = events

    async def get_slider_markup(self, index: int = 0) -> InlineKeyboardMarkup:
        months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
                  "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
        date: datetime.datetime = self.events[index][2]
        inline_kb = InlineKeyboardMarkup(row_width=3)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<<',
            callback_data=event_slider_callback_data.new("PREV", (index - 1))
        ))
        inline_kb.insert(InlineKeyboardButton(
            '{} {}'.format(date.day, months[int(date.month) - 1]),
            callback_data=event_slider_callback_data.new("IGNORE", index)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=event_slider_callback_data.new("NEXT", (index + 1))
        ))
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            'Я приду',
            callback_data=event_slider_callback_data.new("SUB", index)
        ))
        return inline_kb

    async def new_text(self, index: int) -> str:
        return await format_event_extended(self.events[index][1], self.events[index][2], self.events[index][3],
                                           self.events[index][4], self.events[index][5], str(self.events[index][6]))

    async def selection(self, query: CallbackQuery, callback_data: dict) -> tuple:
        return_data: tuple = (False, None)
        if callback_data['action_event_user'] == "IGNORE":
            await query.answer(cache_time=60)
        if callback_data['action_event_user'] == "PREV":
            if int(callback_data['index_event']) >= 0:
                await query.message.edit_text(await self.new_text(int(callback_data['index_event'])), 'HTML',
                                              reply_markup=await self.get_slider_markup(int(callback_data['index_event'])))
        if callback_data['action_event_user'] == "NEXT":
            if int(callback_data['index_event']) <= len(self.events) - 1:
                await query.message.edit_text(await self.new_text(int(callback_data['index_event'])), 'HTML',
                                              reply_markup=await self.get_slider_markup(int(callback_data['index_event'])))

            # В случае если пользователь хочет пойти на событие то функция возвратит id события
        if callback_data['action_event_user'] == "SUB":
            return_data = True, self.events[int(callback_data['index_event'])][0]
        return return_data
