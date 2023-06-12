import csv
import bot.database.database as db


async def get_all_users_info():
    records = await db.any_command("SELECT user_id,surname,first_name,patronymic,"
                                   "birthday,phone_number,about,partner,is_admin,"
                                   "is_plus_user,c.number_plate,c.car_photo_file_id "
                                   "FROM users join car c on c.id = users.car_id")

    with open('users_data.csv', 'w') as f:
        writer = csv.writer(f, dialect=csv.excel)
        columns = (
            "id пользователя", "Фамилия", "Имя", "Отчество",
            "День рождения", "Номер телефона", "Род деятельности",
            "Информация о партнере", "админ", "пользователь+", "гос.номер", "file_id авто")
        writer.writerow(columns)
        for row in records:
            writer.writerow(row)
