import asyncio

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from aiogram.utils.exceptions import MessageCantBeDeleted

import bot.keyboards as kb
from bot.env import Env

from bot.filters.main import IsNotificationGroupCallback
from bot.misc.formatting import replace_markdown_marks


async def answer_on_user_question(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    bot: Bot = callback.bot
    await callback.answer()
    await bot.edit_message_text(
        'Отвечен ✔\n [Пользователю](tg://user?id={})'.format(
            callback_data['user_id']) + '\nСам вопрос:' + await replace_markdown_marks(callback.message.text),
        message_id=callback.message.message_id,
        reply_markup=await kb.question_delete(), chat_id=Env.NOTIFICATION_SUPER_GROUP_ID, parse_mode='MarkdownV2')


async def delete_user_question(callback: CallbackQuery, state: FSMContext):
    bot: Bot = callback.bot
    await callback.answer()
    try:
        await bot.delete_message(chat_id=Env.NOTIFICATION_SUPER_GROUP_ID, message_id=callback.message.message_id)
    except MessageCantBeDeleted:
        print("Сообщение не может быть удалено т.к. истек срок в 48 часов")


def get_notification_handlers(dp: Dispatcher) -> None:
    # callbacks
    dp.register_callback_query_handler(answer_on_user_question, IsNotificationGroupCallback(),
                                       kb.question_answer_callbackdata.filter())
    dp.register_callback_query_handler(delete_user_question, IsNotificationGroupCallback(),
                                       lambda l: l.data == 'delete_question')
