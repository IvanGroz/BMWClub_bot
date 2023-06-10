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
