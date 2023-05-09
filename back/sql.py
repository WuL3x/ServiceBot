# import sqlite3
#
# from aiogram import types
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
#
# from back.main import bot
#
#
# async def client_from_bd(callback: types.CallbackQuery):
#     conn = sqlite3.connect('E:/sqlite3/Servigo')
#     cursor = conn.cursor()
#     orders_zp = "SELECT id_order FROM Orders WHERE id_client=?"
#     orders = cursor.execute(orders_zp, (callback.from_user.id,)).fetchall()
#     buttons = [InlineKeyboardButton(str(order[0]), callback_data=f"Заказ №: {order[0]}") for order in orders]
#     keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
#     await bot.send_message(callback.from_user.id, "Выберите номер заказа:", reply_markup=keyboard)
#     conn.close()
    # id_orders = [row[0] for row in rows]
    # cursor.execute(f'''SELECT Clients.*, Orders.*, Status.*
    #         FROM Clients
    #         JOIN Orders ON Clients.id_client = Orders.id_client
    #         JOIN Status ON Orders.id_status = Status.id_status
    #         WHERE Orders.id_order = <значение id_order>;''')
    # rows = cursor.fetchall()
    # user_data = []
    # for row in rows:
    #     data = {
    #         'device': row[1],
    #         'user_name': row[5],
    #         'dev_name': row[2],
    #         'name': row[3],
    #         'phone': row[4]
    #     }
    #     user_data.append(data)
    # conn.close()
    # return user_data
