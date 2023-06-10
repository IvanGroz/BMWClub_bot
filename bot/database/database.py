# todo: Database engine тут должен быть класс Database
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


async def add_item(state: FSMContext):
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
        cur.execute('SELECT exists(select user_id from users where user_id = {})'.format(user_id_par))
        return cur.fetchone()[0]


async def get_users_birthday(days: int) -> list:
    """Кол-во дней означает для скольких дней от сегодняшнего дня должно быть показано ДР

    Значение 1 - означает только сегодняшнюю дату
    """
    with conn.cursor() as cur:
        date = datetime.date.today()
        arr_users = []
        for i in range(days):
            cur.execute(
                "SELECT user_id,surname,first_name,patronymic,cast(date_part('year',age(birthday)) AS INTEGER)"
                " from users where date_part('day',birthday) = {} "
                "and date_part('month',birthday) = {}".format(
                    date.strftime('%d'), date.strftime('%m')))
            users: tuple = (cur.fetchall(), date.strftime('%m-%d'))
            date += datetime.timedelta(days=1)
            arr_users.append(users)
        return arr_users


def get_users_birthday_notif_on() -> tuple:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id from users where birthday_notif = TRUE and (is_plus_user = TRUE or is_admin = TRUE or is_owner=TRUE)")
        return cur.fetchall()


def set_new_admin(user_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET is_admin = TRUE WHERE user_id = {}".format(user_id))


def find_user(data_fio: list):
    sql_command: str = "select user_id,surname,first_name,patronymic from users where surname = '{}'".format(data_fio[0])
    if len(data_fio) > 1:
        sql_command += "and first_name = '{}'".format(data_fio[1])
        if len(data_fio) > 2:
            sql_command += "and patronymic = '{}'".format(data_fio[2])
    with conn.cursor() as cur:
        cur.execute(sql_command)
        return cur.fetchall()
