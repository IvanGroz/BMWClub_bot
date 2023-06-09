import os
from abc import ABC
from typing import Final


class Env(ABC):
    TOKEN: Final = os.environ.get('TOKEN', '6210427421:AAEpZGEeuxV18QOJO18c5rYp3pxzFXK05z0')
    NOTIFICATION_SUPER_GROUP_ID = os.environ.get('NOTIF_GROUP_ID', -1001813689601)
    QUESTION_THREAD_ID =  os.environ.get('QUESTION_THREAD_ID', 6)
