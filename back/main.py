import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import token

# задаем уровень логирования
logging.basicConfig(level=logging.INFO)
loop = asyncio.new_event_loop()
# создаем объекты бота и диспетчера
bot = Bot(token)
dp = Dispatcher(bot, loop)


    
# запускаем лонг поллинг
if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)