import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database import database


async def start_process_db_polling(bot: Bot):
    scheduler = AsyncIOScheduler(timezone='Asia/Novosibirsk')
    scheduler.add_job(send_birthday_notif, trigger='cron', hour=11, minute=0, start_date=datetime.datetime.now(),
                      kwargs={'bot': bot})
    scheduler.start()


months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
          "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]


async def send_birthday_notif(bot: Bot):
    users = database.get_users_birthday_notif_on()

    birthdays = await database.get_users_birthday(1)
    month, day = str.split(birthdays[0][1], '-')
    str_birthdays_notif: str = 'Сегодня\, {} {} \,день рождения у:'.format(day, months[int(month) - 1])
    for birthday in birthdays[0][0]:  # [номер дня][0 - пользователи , 1 - дата (месяц и день)]
        str_birthdays_notif += '\n[{} {} {}](tg://user?id={})\, исполняется {} лет '.format(birthday[1],
                                                                                            birthday[2],
                                                                                            birthday[3],
                                                                                            birthday[0],
                                                                                            birthday[4])
    for user in users:
        await bot.send_message(user[0], str_birthdays_notif, parse_mode='MarkdownV2')
