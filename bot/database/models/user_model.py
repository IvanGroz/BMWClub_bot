import string


class UserEntity:
    __name: string
    __surname: string
    __patronymic: string

    # def __init__(self, surname: string, name: string, patronymic: string):
    #     self.name = name
    #     self.surname = surname
    #     self.patronymic = patronymic

    def set_name(self, name: string):
        self.__name = name
