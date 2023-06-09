# todo: Database engine тут должен быть класс Database
import datetime

import psycopg2
from aiogram.dispatcher import FSMContext
from psycopg2._psycopg import *


async def start():
    global db, cur
    try:
        # пытаемся подключиться к базе данных
        db = psycopg2.connect('postgresql://postgres:1824@localhost:5432/BMW_Club_NSK')
        db.set_session(autocommit=True)
        cur = db.cursor()
    except:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database')


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
        cur.execute(sql_insert)

    db.commit()


async def is_admin(user_id_par) -> bool:
    cur.execute('select is_admin from users where user_id ={}'.format(user_id_par))
    return cur.fetchone()[0]


async def is_plus_user(user_id_par) -> bool:
    cur.execute('select is_plus_user from users where user_id ={}'.format(user_id_par))
    return cur.fetchone()[0]


async def is_owner(user_id_par) -> bool:
    cur.execute('select is_owner from users where user_id ={}'.format(user_id_par))
    return cur.fetchone()[0]


async def is_registered(user_id_par) -> bool:
    cur.execute('SELECT exists(select user_id from users where user_id = {})'.format(user_id_par))
    return cur.fetchone()[0]
