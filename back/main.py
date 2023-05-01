import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from config import token

storage = MemoryStorage()


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