import datetime


async def format_birthday(birthdays, day) -> str:
    text: str = 'В эту дату\, день рождения у:'
    if len(birthdays[day][0]) != 0:
        for birthday in birthdays[day][0]:  # [номер дня][0 - пользователи , 1 - дата (месяц и день)]
            text += '\n[{} {} {}](tg://user?id={})\, исполняется {} '.format(birthday[1],
                                                                             birthday[2],
                                                                             birthday[3],
                                                                             birthday[0],
                                                                             birthday[4])
    else:
        text = 'В этот день ни у кого дня рождения нет\!'
    return text


async def format_birthday_by_fio(birthday) -> str:
    text: str = 'Дата рождения пользователя:{}'.format(birthday[0][5].strftime('%Y\-%m\-%d'))
    if len(birthday) != 0:
        text += '\n[{} {} {}](tg://user?id={})\, исполняется {} '.format(birthday[0][1],
                                                                         birthday[0][2],
                                                                         birthday[0][3],
                                                                         birthday[0][0],
                                                                         birthday[0][4])
    else:
        text = 'В этот день ни у кого дня рождения нет\!'
    return text


async def replace_markdown_marks(string: str):
    strings_replace = ['_', '*', '[', ']', '(', ')', '~', '`', '>',
                       '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for symbol in strings_replace:  # Экранируем спец символы для ТГ-разметки сообщений
        string = string.replace(symbol, '\\' + symbol)
    return string


async def format_founded_users(users: list, command: str):
    text: str = 'Список найденных пользователей:'
    users_fio_id: dict = {}
    if len(users) == 0:
        text += '\nПуст'
    for user in users:
        user_link = '[{} {} {}](tg://user?id={})'.format(user[1],
                                                         user[2],
                                                         user[3],
                                                         user[0])
        text += '\n' + user_link + ' \n\-\> {}{} \<\-\n\n'.format(command, user[0])
        users_fio_id[str(user[0])] = user_link
    return text, users_fio_id


async def format_event(title: str, date: datetime.datetime, time: datetime.time | str, location: str,
                       description: str) -> str:
    text: str = title + '\n'
    text += '\nЛокация: ' + location
    text += '\n\nВремя: ' + date.strftime('%m/%d')
    if type(time) == datetime.time:
        text += ',' + time.strftime('%H:%M')
    else:
        text += ',' + time
    text += '\n\nОписание:\n' + description
    return text


async def format_event_extended(title: str, date: datetime.datetime, time: datetime.time | str, location: str,
                                description: str, amount_users) -> str:
    text: str = await format_event(title, date, time, location, description)
    text += '\n Сколько придет человек: ' + str(amount_users)
    return text


async def user_info(user):
    birthday: datetime.date = user[4]

    text: str = 'Информация о пользователе <a href="tg://user?id={}">{} {} {}</a>:\n' \
                "\nДата рождения: {}\n" \
                "\nНомер телефона: {}\n" \
                "\nРод деятельности:{}\n" \
                "\nИнформация о партнерстве:{}\n" \
                "\nАдминистратор:{}\n" \
                "\nПользователь с расширенным функционалом:{}\n" \
                "\nГос.номер: {}\n" \
                "".format(user[0], user[1], user[2], user[3], birthday.strftime('%Y-%m-%d'),
                          user[5], user[6], user[7], user[8], user[9], user[10])
    return text, user[11]  # Описание пользователя и фото авто
