from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

import bot.database.database as db


async def get_all_users_info():
    records = await db.any_command("SELECT user_id,surname,first_name,patronymic,"
                                   "birthday,phone_number,about,partner,is_admin,"
                                   "is_plus_user,c.number_plate,c.car_photo_file_id "
                                   "FROM users join car c on c.id = users.car_id")
    columns = (
        "id пользователя", "Фамилия", "Имя", "Отчество",
        "День рождения", "Номер телефона", "Род деятельности",
        "Информация о партнере", "админ", "пользователь+", "Гос.номер", "file_id авто")
    file_name = 'all_users_data.xlsx'
    workbook = Workbook()
    workbook.save(file_name)
    workbook.create_sheet('data', 0)
    worksheet: Worksheet = workbook['data']
    worksheet.column_dimensions['A'].width = 20
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 20
    worksheet.column_dimensions['D'].width = 20
    worksheet.column_dimensions['E'].width = 15
    worksheet.column_dimensions['F'].width = 15
    worksheet.column_dimensions['G'].width = 40
    worksheet.column_dimensions['H'].width = 40
    worksheet.column_dimensions['I'].width = 10
    worksheet.column_dimensions['J'].width = 15
    worksheet.column_dimensions['K'].width = 10
    worksheet.column_dimensions['L'].width = 85
    worksheet.append(columns)
    for row in records:
        worksheet.append(row)
    workbook.save(file_name)
    workbook.close()


