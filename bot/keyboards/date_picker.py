import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery

date_picker_callback = CallbackData('date_picker', 'act', 'year', 'month', 'day')
ignore_callback = date_picker_callback.new("IGNORE", -1, -1, -1)  # применяется для кнопок без ответа


class DatePicker:
    months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

    def __init__(self, year: int = datetime.now().year, month: int = datetime.now().month):
        self.year = year
        self.month = month

    async def start_picker(
            self,
            year: int = datetime.now().year - 20  # 20 для того чтобы выбор года начинался для человека от 18 лет
    ) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=6)
        # first row - years
        inline_kb.row()
        for value in range(year - 3, year + 3):
            inline_kb.insert(InlineKeyboardButton(
                str(value),
                callback_data=date_picker_callback.new("SET-YEAR", value, -1, -1)
            ))
        # nav buttons
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<<',
            callback_data=date_picker_callback.new("PREV-YEARS", year, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=date_picker_callback.new("NEXT-YEARS", year, -1, -1)
        ))

        return inline_kb

    async def _get_month_kb(self, year: int) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=6)
        # первый ряд это года
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(
            str(year),
            callback_data=date_picker_callback.new("START", year, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        # два ряда кнопок по 6 месяцев
        inline_kb.row()
        for month in self.months[0:6]:
            inline_kb.insert(InlineKeyboardButton(
                month,
                callback_data=date_picker_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1)
            ))
        inline_kb.row()
        for month in self.months[6:12]:
            inline_kb.insert(InlineKeyboardButton(
                month,
                callback_data=date_picker_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1)
            ))
        return inline_kb

    async def _get_days_kb(self, year: int, month: int):
        inline_kb = InlineKeyboardMarkup(row_width=7)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            str(year),
            callback_data=date_picker_callback.new("START", year, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            self.months[month - 1],
            callback_data=date_picker_callback.new("SET-YEAR", year, -1, -1)
        ))
        inline_kb.row()
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if day == 0:
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=date_picker_callback.new("SET-DAY", year, month, day)
                ))
        return inline_kb

    async def process_selection(self, query: CallbackQuery, callback_data: dict) -> tuple:
        return_data: tuple = (False, None)
        if callback_data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        if callback_data['act'] == "SET-YEAR":
            await query.message.edit_reply_markup(await self._get_month_kb(int(callback_data['year'])))
        if callback_data['act'] == "PREV-YEARS":
            new_year = int(callback_data['year']) - 5
            await query.message.edit_reply_markup(await self.start_picker(new_year))
        if callback_data['act'] == "NEXT-YEARS":
            new_year = int(callback_data['year']) + 5
            await query.message.edit_reply_markup(await self.start_picker(new_year))
        if callback_data['act'] == "START":
            await query.message.edit_reply_markup(await self.start_picker(int(callback_data['year'])))
        if callback_data['act'] == "SET-MONTH":
            await query.message.edit_reply_markup(
                await self._get_days_kb(int(callback_data['year']), int(callback_data['month'])))
        if callback_data['act'] == "SET-DAY":
            await query.message.delete_reply_markup()  # удаление инлайн-клавиатуры
            print("birthday_input \n" + datetime.now().strftime('[%Y-%m-%d]:[%H-%M]') + " idUser:" +
                  str(query.from_user.id) + "picked data:" + callback_data['year'] + "-" + callback_data[
                      'month'] + "-" + callback_data['day'])
            return_data = True, datetime(int(callback_data['year']), int(callback_data['month']),
                                         int(callback_data['day']))
        return return_data
