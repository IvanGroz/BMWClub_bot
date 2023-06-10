import os
from abc import ABC
from typing import Final


class Env(ABC):
    TOKEN: Final = os.environ.get('TOKEN', '6210427421:AAEpZGEeuxV18QOJO18c5rYp3pxzFXK05z0')
    NOTIFICATION_SUPER_GROUP_ID = os.environ.get('NOTIF_GROUP_ID', -1001813689601)
    QUESTION_THREAD_ID = os.environ.get('QUESTION_THREAD_ID', 6)
    NEW_MEMBER_THREAD_ID = os.environ.get('NEW_MEMBER_THREAD_ID', 8)
    NEW_PARTNER_THREAD_ID = os.environ.get('NEW_PARTNER_THREAD_ID', 10)
    SECRET_PASSWORD = os.environ.get('SECRET_PASSWORD', '3487bmw_club-passw037tyfggfdsz')
    CONNECTION_URL = os.environ.get('CONNECTION_URL', 'postgresql://postgres:1824@localhost:5432/BMW_Club_NSK')
