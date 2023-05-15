import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from config import token

storage = MemoryStorage()
def order_num():
    conn = sqlite3.connect('E:/sqlite3/Servigo')
    cursor = conn.cursor()
    order_id = "SELECT id_order FROM Orders ORDER BY id_order DESC LIMIT 1"
    cursor.execute(order_id)
    last_order = cursor.fetchone()

    # Проверка наличия последнего заказа
    if last_order is not None:
        last_order_number = last_order[0]
        next_order_number = last_order_number + 1
    else:
        next_order_number = 1  # Если нет последнего заказа, начинаем с 1
    return next_order_number
def generate_order_id():
    global order_id
    order_id = order_num()
    return f'{order_id:06}'


# задаем уровень логирования
logging.basicConfig(level=logging.INFO)
loop = asyncio.new_event_loop()

# создаем объекты бота и диспетчера
bot = Bot(token)
dp = Dispatcher(bot, loop, storage=storage)

# запускаем лонг поллинг
if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)