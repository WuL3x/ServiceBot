from aiogram import types

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InputFile, WebAppInfo
from aiogram.utils import executor
from aiogram.utils.exceptions import CantInitiateConversation, MessageCantBeDeleted, MessageToDeleteNotFound
from main import bot, dp
from keyboards import bt_sec

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f'''Привет, {message.from_user.first_name}!\nЯ бот, с помощью которого можно узнать статус 
своего заказа''', reply_markup=bt_sec)

@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.chat.id, msg.text)