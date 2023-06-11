async def format_birthday(birthdays, day) -> str:
    text: str = 'В эту дату\, день рождения у:'
    if len(birthdays[day][0]) != 0:
        for birthday in birthdays[day][0]:  # [номер дня][0 - пользователи , 1 - дата (месяц и день)]
            text += '\n[{} {} {}](tg://user?id={})\, исполняется {} лет '.format(birthday[1],
                                                                                 birthday[2],
                                                                                 birthday[3],
                                                                                 birthday[0],
                                                                                 birthday[4])
    else:
        text = 'В этот день ни у кого дня рождения нет\!'
    return text


async def format_founded_users(users: list, command: str):
    text: str = 'Список найденных пользователей:'
    users_fio_id: dict = {}
    for user in users:
        user_link = '[{} {} {}](tg://user?id={})'.format(user[1],
                                                         user[2],
                                                         user[3],
                                                         user[0])
        text += '\n' + user_link + ' \n\-\> {}{} \<\-\n'.format(command,
                                                                user[0])
        users_fio_id[str(user[0])] = user_link
    return text, users_fio_id
