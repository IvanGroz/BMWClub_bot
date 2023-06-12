from aiogram import Dispatcher, Bot
from aiogram.types import *
import bot.strings as st
import bot.keyboards as kb
from bot.filters.main import *
from bot.database import database as db
from bot.misc.anti_swearing import is_swearing, censoring_text


async def watch_events(message: Message, state: FSMContext):
    bot: Bot = message.bot
    list_event = await db.get_list_event()


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
        await bot.delete_message(message.chat.id, message.message_id)


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(watch_events, IsRegularUserOnly(), content_types=['text'],
                                text='Ближайшие мероприятия')
    dp.register_message_handler(watch_events, IsRegularUserOnly(), content_types=['text'],
                                text='Отключить уведомления')
    dp.register_message_handler(watch_events, IsRegularUserOnly(), content_types=['text'],
                                text='Включить уведомления')
    dp.register_message_handler(swear_check, chat_type=[ChatType.SUPERGROUP, ChatType.GROUP], content_types=['text'])
