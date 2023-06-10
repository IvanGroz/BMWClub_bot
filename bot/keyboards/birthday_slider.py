from aiogram.types import *
from aiogram.utils.callback_data import *

slider_callback = CallbackData('slider', 'action', 'days')


class BirthdaySlider:
    def __init__(self, birthdays):
        self.birthdays = birthdays

    async def get_slider_markup(self, day_ind: int = 0) -> InlineKeyboardMarkup:
        months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
                  "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
        month, day = str.split(self.birthdays[day_ind][1], '-')
        inline_kb = InlineKeyboardMarkup(row_width=3)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<<',
            callback_data=slider_callback.new("PREV", (day_ind - 1))
        ))
        inline_kb.insert(InlineKeyboardButton(
            '{} {}'.format(day, months[int(month) - 1]),
            callback_data=slider_callback.new("IGNORE", day_ind)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=slider_callback.new("NEXT", (day_ind + 1))
        ))
        return inline_kb

    async def new_text(self, day: int) -> str:
        text: str = 'В эту дату день рождения у:'
        for birthday in self.birthdays[day][0]:  # [номер дня][0 - пользователи , 1 - дата (месяц и день)]
            text += '\n[{} {} {}](tg://user?id={})\, исполняется {} лет '.format(birthday[1],
                                                                                 birthday[2],
                                                                                 birthday[3],
                                                                                 birthday[0],
                                                                                 birthday[4])
        return text

    async def selection(self, query: CallbackQuery, callback_data: dict):
        if callback_data['action'] == "IGNORE":
            await query.answer(cache_time=60)
        if callback_data['action'] == "PREV":
            if int(callback_data['days']) >= 0:
                await query.message.edit_text(await self.new_text(int(callback_data['days'])), 'MarkdownV2',
                                              reply_markup=await self.get_slider_markup(int(callback_data['days'])))
        if callback_data['action'] == "NEXT":
            if int(callback_data['days']) <= 13:
                await query.message.edit_text(await self.new_text(int(callback_data['days'])), 'MarkdownV2',
                                              reply_markup=await self.get_slider_markup(int(callback_data['days'])))
