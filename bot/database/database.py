import datetime

import psycopg2
from aiogram.dispatcher import FSMContext
from psycopg2._psycopg import *

conn: connection


def start():
    global conn
    try:
        # пытаемся подключиться к базе данных
        conn = psycopg2.connect('postgresql://postgres:1824@localhost:5432/BMW_Club_NSK')
        conn.set_session(autocommit=True)
    except Exception as e:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database:' + str(e))


async def add_user(state: FSMContext):
    async with state.proxy() as data:
        birthday: datetime.datetime = data['birthday']
        sql_insert = "select insert_user_data({},'{}','{}','{}','{}','{}','{}','{}','{}','{}')". \
            format(data['user_id'],
                   data['name'],
                   data['surname'],
                   data['patronymic'],
                   birthday.strftime('%Y-%m-%d'),
                   data['about'],
                   data['photo'],
                   data['number_plate'],
                   data['phone_number'],
                   data['partner'])
        with conn.cursor() as cur:
            cur.execute(sql_insert)

    conn.commit()


async def delete_user_from_db(user_id_par):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM car c WHERE id IN (SELECT car_id FROM users WHERE user_id = {})'.format(user_id_par))
    conn.commit()


async def is_admin(user_id_par) -> bool:
    with conn.cursor() as cur:
        cur.execute('select is_admin from users where user_id ={}'.format(user_id_par))
        return cur.fetchone()[0]


async def is_plus_user(user_id_par) -> bool:
    with conn.cursor() as cur:
        cur.execute('select is_plus_user from users where user_id ={}'.format(user_id_par))
        return cur.fetchone()[0]


async def is_owner(user_id_par) -> bool:
    with conn.cursor() as cur:
        cur.execute('select is_owner from users where user_id ={}'.format(user_id_par))
        return cur.fetchone()[0]


async def is_registered(user_id_par) -> bool:
    with conn.cursor() as cur:
        cur.execute('select exists(select user_id from users where user_id = {})'.format(user_id_par))
        return cur.fetchone()[0]


async def get_user_by_id(user_id):
    with conn.cursor() as cur:
        cur.execute('SELECT user_id,surname, first_name, patronymic, birthday, '
                    'phone_number,about,partner,is_admin, is_plus_user,'
                    ' c.number_plate, c.car_photo_file_id FROM users join car c on c.id = users.car_id'
                    ' where user_id = {}'.format(user_id))
        return cur.fetchone()


async def get_users_birthday(days: int) -> list:
    """Кол-во дней означает для скольких дней от сегодняшнего дня должно быть показано ДР

    Значение 1 - означает только сегодняшнюю дату
    """
    with conn.cursor() as cur:
        date = datetime.date.today()
        arr_users = []
        for i in range(days):
            cur.execute(
                "SELECT user_id,surname,first_name,patronymic,cast(date_part('year',age(birthday)) AS INTEGER)+1"
                " from users where date_part('day',birthday) = {} "
                "and date_part('month',birthday) = {}".format(
                    date.strftime('%d'), date.strftime('%m')))
            users: tuple = (cur.fetchall(), date.strftime('%m-%d'))
            date += datetime.timedelta(days=1)
            arr_users.append(users)
        return arr_users


async def get_users_birthday_id(user_id) -> list:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id,surname,first_name,patronymic,cast(date_part('year',age(birthday)) AS INTEGER)+1,birthday"
            " from users where user_id = {}".format(
                user_id))
        return cur.fetchall()


def get_users_birthday_notif_on() -> tuple:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id from users where birthday_notif = TRUE and (is_plus_user = TRUE or is_admin = TRUE or is_owner=TRUE)")
        return cur.fetchall()


def get_user_birthday_notif_on(user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT birthday_notif from users where user_id = {}".format(user_id))
        return cur.fetchall()


def set_new_admin(user_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET is_admin = TRUE WHERE user_id = {}".format(user_id))


def delete_admin(user_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET is_admin = FALSE WHERE user_id = {}".format(user_id))


def set_new_plus_user(user_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET is_plus_user = TRUE WHERE user_id = {}".format(user_id))


def delete_plus_user(user_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET is_plus_user = FALSE WHERE user_id = {}".format(user_id))


def find_user(data_fio: list):
    sql_command: str = "select user_id,surname,first_name,patronymic from users where "
    if data_fio[0].lower() != 'нет':
        sql_command += "surname = '{}'".format(data_fio[0])
    if len(data_fio) > 1:
        if data_fio[0].lower() != 'нет':
            sql_command += " and "
        if data_fio[1].lower() != 'нет':
            sql_command += "first_name = '{}' ".format(data_fio[1])
        if len(data_fio) > 2:
            if data_fio[1].lower() != 'нет' and data_fio[0].lower() != 'нет':
                sql_command += " and "
            sql_command += "patronymic = '{}'".format(data_fio[2])
    with conn.cursor() as cur:
        cur.execute(sql_command)
        return cur.fetchall()


def find_user_by_car(number_plate: str):
    with conn.cursor() as cur:
        cur.execute('SELECT user_id,surname, first_name, patronymic, birthday, '
                    'phone_number,about,partner,is_admin, is_plus_user,'
                    ' c.number_plate, c.car_photo_file_id FROM users join car c on c.id = users.car_id '
                    " WHERE number_plate = '{}'".format(number_plate))
        return cur.fetchone()


def find_admins():
    with conn.cursor() as cur:
        cur.execute("SELECT user_id,surname,first_name,patronymic FROM users where is_admin = TRUE")
        return cur.fetchall()


def find_plus_users():
    with conn.cursor() as cur:
        cur.execute("SELECT user_id,surname,first_name,patronymic FROM users where is_plus_user = TRUE")
        return cur.fetchall()


async def add_event(state: FSMContext):
    async with state.proxy() as data:
        date: datetime.datetime = data['date']
        sql_insert = "INSERT INTO events(title, date, time, location, description) VALUES ('{}','{}','{}','{}','{}')". \
            format(data['title'],
                   date.strftime('%Y-%m-%d'),
                   data['time'],
                   data['location'],
                   data['description'])
        with conn.cursor() as cur:
            cur.execute(sql_insert)


async def get_list_event(all: bool = False):
    sql_command: str = "WHERE date >=(SELECT CURRENT_DATE)"
    with conn.cursor() as cur:
        if all:
            cur.execute("SELECT * from events  ORDER BY date ASC ")
        else:
            cur.execute("SELECT * from events {} ORDER BY date ASC ".format(sql_command))
        return cur.fetchall()


async def get_tomorrow_events():
    date = datetime.date.today() + datetime.timedelta(days=1)
    with conn.cursor() as cur:
        cur.execute("SELECT * from events WHERE date = '{}'".format(date.strftime('%Y-%m-%d')))
        return cur.fetchall()


def delete_event(event_id):
    with conn.cursor() as cur:
        cur.execute("DELETE  FROM events WHERE id ={}".format(event_id))


def edit_event(event_id, location=None, date=None, time=None, description=None, title=None):
    sql_text = "UPDATE events SET "
    if location is not None:
        sql_text += "location = '{}'".format(location)
    if date is not None:
        sql_text += "date = '{}',time = '{}'".format(date, time)
    if title is not None:
        sql_text += "title = '{}',description = '{}'".format(title, description)
    sql_text += "WHERE id = {}".format(event_id)
    with conn.cursor() as cur:
        cur.execute(sql_text)


def get_users_event_notif_on() -> tuple:
    with conn.cursor() as cur:
        cur.execute("SELECT user_id from users where event_notif = TRUE")
        return cur.fetchall()


def get_one_user_event_notif_on(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT event_notif from users where user_id = {}".format(user_id))
        return cur.fetchall()


async def unsubscribe_on_event(user_id, event_id):
    with conn.cursor() as cur:
        cur.execute("SELECT unsubscribe_on_event({},{})".format(user_id, event_id))


async def subscribe_on_event(user_id, event_id):
    with conn.cursor() as cur:
        cur.execute("SELECT subscribe_on_event({},{})".format(user_id, event_id))


async def is_subscribe_on_event(event_id, user_id) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT is_subscribe_on_event({},{})".format(user_id, event_id))
        return (cur.fetchall())[0][0]


async def any_command(sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)
        try:
            return cur.fetchall()
        except ProgrammingError:
            return None


async def any_command_get_bool(sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)
        try:
            return (cur.fetchall())[0][0]
        except ProgrammingError:
            return None
