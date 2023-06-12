import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from bot.misc.formatting import *

event_slider_admin_callback = CallbackData('slider_event_admin', 'action_event', 'index')


class EventsSliderAdmin:
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
            callback_data=event_slider_admin_callback.new("PREV", (index - 1))
        ))
        inline_kb.insert(InlineKeyboardButton(
            '{} {}'.format(date.day, months[int(date.month) - 1]),
            callback_data=event_slider_admin_callback.new("IGNORE", index)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=event_slider_admin_callback.new("NEXT", (index + 1))
        ))
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            'Редактировать',
            callback_data=event_slider_admin_callback.new("EDIT", index)
        ))
        return inline_kb

    async def new_text(self, index: int) -> str:
        return await format_event_extended(self.events[index][1], self.events[index][2], self.events[index][3],
                                           self.events[index][4], self.events[index][5], str(self.events[index][6]))

    async def selection(self, query: CallbackQuery, callback_data: dict) -> tuple:
        return_data: tuple = (False, None)
        if callback_data['action_event'] == "IGNORE":
            await query.answer(cache_time=60)
        if callback_data['action_event'] == "PREV":
            if int(callback_data['index']) >= 0:
                await query.message.edit_text(await self.new_text(int(callback_data['index'])), 'HTML',
                                              reply_markup=await self.get_slider_markup(int(callback_data['index'])))
        if callback_data['action_event'] == "NEXT":
            if int(callback_data['index']) <= len(self.events) - 1:
                await query.message.edit_text(await self.new_text(int(callback_data['index'])), 'HTML',
                                              reply_markup=await self.get_slider_markup(int(callback_data['index'])))

            # В случае если админ хочет отредактировать событие то функция возвратит id события
        if callback_data['action_event'] == "EDIT":
            return_data = True, self.events[int(callback_data['index'])][0]
        return return_data
