import time

from aiogram import Dispatcher, Bot
from aiogram.types import *
import bot.strings as st
import bot.keyboards as kb
from bot.filters.main import *
from bot.database import database as db
from bot.keyboards.events_slider import EventsSlider, event_slider_callback_data
from bot.misc.anti_swearing import is_swearing, censoring_text
from bot.misc.formatting import format_event_extended
import datetime, time


async def watch_events(message: Message, state: FSMContext):
    bot: Bot = message.bot
    list_event = await db.get_list_event()

    event_slider_user = EventsSlider(list_event, message.from_user.id)
    await bot.send_message(message.chat.id,
                           await format_event_extended(list_event[0][1], list_event[0][2], list_event[0][3],
                                                       list_event[0][4], list_event[0][5], list_event[0][6]),
                           ParseMode.HTML,
                           reply_markup=await event_slider_user.get_slider_markup()
                           )


async def event_slider_callback(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    subscribe, event_id = await EventsSlider(await db.get_list_event(), callback_query.from_user.id).selection(
        callback_query, callback_data)
    await callback_query.answer()
    if subscribe:
        await callback_query.bot.send_message(callback_query.from_user.id, 'Будем рады Вас видеть\)')


async def off_events_notif(message: Message, state: FSMContext):
    await db.any_command("UPDATE users SET event_notif = false WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления отключены', reply_markup=await kb.event_menu(
        db.get_user_event_notif_on(message.from_user.id)[0]))


async def on_events_notif(message: Message, state: FSMContext):
    await db.any_command("UPDATE users SET event_notif = true WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления включены', reply_markup=await kb.event_menu(
        db.get_user_event_notif_on(message.from_user.id)[0]))


async def swear_check(message: Message, state: FSMContext):
    bot: Bot = message.bot
    if await is_swearing(message.text):
        await bot.send_message(message.chat.id,
                               "*Не материтесь\! Иначе можете быть заблокированы\!*"
                               "\nПользователь, [{0}](tg://user?id={1}),сказал:\n".format(
                                   message.from_user.full_name, message.from_user.id) + await censoring_text(
                                   message.text),
                               'MarkdownV2')
        block = await db.any_command_get_bool("SELECT block_for_swearing({})".format(message.from_user.id))
        await bot.delete_message(message.chat.id, message.message_id)
        if block:
            until: datetime = datetime.date.today() + datetime.timedelta(days=7)
            await bot.restrict_chat_member(message.chat.id, message.from_user.id,
                                           ChatPermissions(False, False, False, False, False, False, False, False,
                                                           False, False, False, False, False, False, False), None,
                                           int(time.mktime(until.timetuple()))
                                           )
            # чтобы убрать пользователя из бана Настройки группы -> разрешения -> Исключения


async def event_menu(message: Message, state: FSMContext):
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id, 'Выберите пункт меню',
                           reply_markup=await kb.event_menu(db.get_user_event_notif_on(message.from_user.id)[0]))


async def off_events_notif(message: Message):
    await db.any_command("UPDATE users SET event_notif = false WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления отключены', reply_markup=await kb.event_menu(
        db.get_user_event_notif_on(message.from_user.id)[0]))


async def on_events_notif(message: Message):
    await db.any_command("UPDATE users SET event_notif = true WHERE user_id = {}".format(message.from_user.id))
    await message.bot.send_message(message.chat.id, 'Уведомления включены', reply_markup=await kb.event_menu(
        db.get_user_event_notif_on(message.from_user.id)[0]))


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(watch_events, IsRegularUserOrPlusUser(), content_types=['text'],
                                text='Ближайшие мероприятия')
    dp.register_message_handler(off_events_notif, IsRegularUserOrPlusUser(), content_types=['text'],
                                text='Отключить уведомления')
    dp.register_message_handler(on_events_notif, IsRegularUserOrPlusUser(), content_types=['text'],
                                text='Включить уведомления')
    dp.register_message_handler(event_menu, IsRegularUserOrPlusUser(), text='Мероприятия клуба')
    dp.register_message_handler(swear_check, chat_type=[ChatType.SUPERGROUP, ChatType.GROUP],
                                content_types=['text'])
    dp.register_callback_query_handler(event_slider_callback, IsRegularUserOrPlusUser(),
                                       event_slider_callback_data.filter())
    # todo заказ одежды,удаление админа и пользователя +, натсроика мата
    # todo запитьсь в эксель,поиск ДР по имени
