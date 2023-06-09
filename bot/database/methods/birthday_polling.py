import datetime
import time
from multiprocessing import *
import aioschedule as schedule
from aiogram import Bot
from psycopg2._psycopg import *

from bot.database import database


async def start_process_db_polling(bot: Bot):
    schedule.every().day.at("11:00").do(send_birthday_notif, bot)
    # schedule.every(5).seconds.do(send_birthday_notif, bot)
    while True:
        await schedule.run_pending()
        time.sleep(1)


async def send_birthday_notif(bot: Bot):
    users = database.get_users_birthday_notif_on()
    birthdays = database.get_today_birthday()
    str_birthdays_notif: str = 'Сегодня день рождения у:'
    for birthday in birthdays:
        str_birthdays_notif += '\n[{} {} {}](tg://user?id={})\, исполняется {} лет '.format(birthday[1], birthday[2],
                                                                                            birthday[3], birthday[0],
                                                                                            birthday[4])
    for user in users:
        await bot.send_message(user[0], str_birthdays_notif, parse_mode='MarkdownV2')
