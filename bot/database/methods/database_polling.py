from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database import database
from bot.misc.formatting import *


async def start_process_db_polling(bot: Bot):
    scheduler = AsyncIOScheduler(timezone='Asia/Novosibirsk')
    scheduler.add_job(send_birthday_notif, trigger='cron', hour=11, minute=0, start_date=datetime.datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(send_event_notification, trigger='cron', hour=13, minute=0, start_date=datetime.datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(reset_swearing, 'interval', weeks=1)
    scheduler.start()


months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
          "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]


async def reset_swearing():
    await database.any_command("TRUNCATE swearing_users")


async def send_birthday_notif(bot: Bot):
    birthdays = await database.get_users_birthday(1)
    if len(birthdays[0][0]) == 0:
        return
    users = database.get_users_birthday_notif_on()
    month, day = str.split(birthdays[0][1], '-')
    str_birthdays_notif: str = 'Сегодня\, {} {} \,день рождения у:'.format(day, months[int(month) - 1])
    for birthday in birthdays[0][0]:  # [номер дня][0 - пользователи , 1 - дата (месяц и день)]
        str_birthdays_notif += '\n[{} {} {}](tg://user?id={})\, исполняется {} '.format(birthday[1],
                                                                                        birthday[2],
                                                                                        birthday[3],
                                                                                        birthday[0],
                                                                                        birthday[4])
    for user in users:
        await bot.send_message(user[0], str_birthdays_notif, parse_mode='MarkdownV2')


async def send_event_notification(bot: Bot):
    events = await database.get_tomorrow_event()
    if len(events) == 0:
        return
    users = database.get_users_event_notif_on()
    event_notif_str: str = "Напоминание о грядущем мероприятиях, уже завтра:\n"
    for event in events:
        event_notif_str += await format_event_extended(event[1], event[2], event[3], event[4], event[5], event[6])
        event_notif_str += '\n------------\n'
    for user in users:
        await bot.send_message(user[0], event_notif_str, parse_mode='HTML')
