import time
import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

from back.keyboards import kb_dev, kb1
from config import CHANNEL_ID
from keyboards import bt_sec
from main import bot, dp

button_cancel = types.InlineKeyboardButton('Отмена', callback_data='cancel')
cancelButton = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)

@dp.callback_query_handler(text=['Меню'])
async def main_menu(callback: types.callback_query):
    await bot.send_message(callback.from_user.id, reply_markup=kb1, text='Выберите пункт меню 👇🏻')


def register():
    class RepairForm(StatesGroup):

        device = State()  # выбор типа устройства
        dev_name = State()
        issue = State()
        name = State()
        phone = State()
        confirm = State()

    @dp.message_handler(state='*', commands='cancel')
    @dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
    async def cancel(message: types.message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return

        await bot.send_message(message.from_user.id, text='''Отмена отправки⛔''', reply_markup=bt_sec)
        time.sleep(1)
        await main_menu(message)
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == 'register', state="*")
    async def register_order(callback: types.CallbackQuery, state: FSMContext):
        await bot.send_message(callback.from_user.id,
                               f'{callback.from_user.username}, Укажите тип и название устройства.',
                               reply_markup=cancelButton)
        await bot.send_message(callback.from_user.id, 'Выберите тип устройства:', reply_markup=kb_dev)
        async with state.proxy() as data:
            data['user_name'] = callback.from_user.username
            data['id_order'] = str(uuid.uuid4().int)[:6]
        await RepairForm.device.set()

    @dp.callback_query_handler(lambda c: c.data.startswith('device:'), state=RepairForm.device)
    async def process_device(callback: types.CallbackQuery, state: FSMContext):
        data = callback.data.split(':')
        device = data[1]
        # сохраняем данные в состоянии
        await state.update_data(device=device)

        if device == 'Компьютер':
            await bot.send_message(callback.from_user.id,
                                   "Пожалуйста, укажите что произошло с ПК..",
                                   reply_markup=cancelButton)
            await RepairForm.issue.set()


        else:
            await bot.send_message(callback.from_user.id,
                                   "Пожалуйста, напишите полное название устройства. ",
                                   reply_markup=cancelButton)
            await RepairForm.dev_name.set()

    @dp.message_handler(state=RepairForm.dev_name)
    async def process_dev_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['dev_name'] = message.text
        await bot.send_message(message.from_user.id, "Пожалуйста, опишите проблему.", reply_markup=cancelButton)
        await RepairForm.issue.set()

    @dp.message_handler(state=RepairForm.issue)
    async def process_issue(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['issue'] = message.text

        await message.reply("Введите Ваше имя.", reply=False, reply_markup=cancelButton)
        await RepairForm.name.set()

    @dp.message_handler(state=RepairForm.name)
    async def process_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['name'] = message.text

        await message.reply("Введите Ваш номер телефона.", reply=False, reply_markup=cancelButton)
        await RepairForm.phone.set()

    @dp.message_handler(state=RepairForm.phone)
    async def process_phone(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['phone'] = message.text

            # формируем сообщение
            text = f"Заявка\n"
            text += f"Ремонт {data['device']}а:\n"
            text += f"Номер заявки: {data['id_order']}\n"
            if data['device'] != 'Компьютер':
                text += f"Название устройства: {data['dev_name']}\n"
            text += f"Описание проблемы: {data['issue']}\n"
            text += f"Имя: {data['name']}\n"
            text += f"Телефон: {data['phone']}\n"

            kb_con = types.InlineKeyboardMarkup()
            kb_con.insert(types.InlineKeyboardButton(text="Все верно", callback_data='confirm:verno'))
            kb_con.add(types.InlineKeyboardButton(text="Нет. Есть ошибка", callback_data='confirm:error'))

            # отправляем сообщение пользователю
            await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode=ParseMode.HTML,
                                   reply_markup=kb_con)
        await RepairForm.confirm.set()

    @dp.callback_query_handler(state=RepairForm.confirm)
    async def process_confirm(callback: types.CallbackQuery, state: FSMContext):
        # обрабатываем ответ на кнопку
        if callback.data.split(':')[1] == 'verno':
            await bot.send_message(callback.from_user.id, "Спасибо за заявку! В скором времени с вами свяжется менеджер")
            async with state.proxy() as data:
                text = f"Заявка на ремонт {data['device']}а:\n"
                text += f"TG user name: @{data['user_name']}\n"
                text += f"TG_ID: {callback.from_user.id}\n"
                text += f"Номер заявки: {data['id_order']}\n"
                if data['device'] != 'Компьютер':
                    text += f"Название устройства: {data['dev_name']}\n"
                text += f"Описание проблемы: {data['issue']}\n"
                text += f"Имя: {data['name']}\n"
                text += f"Телефон: {data['phone']}\n"
            kb_chat = InlineKeyboardMarkup()
            kb_chat.add(InlineKeyboardButton(text="Перейти в чат",
                                             url=f"t.me/{callback.from_user.username}"))

            # Отправляем сообщение на заданный вами чат или группу в Telegram
            await bot.send_message(CHANNEL_ID, text, reply_markup=kb_chat)

        elif callback.data.split(':')[1] == 'error':
            reank = types.InlineKeyboardMarkup()
            reank.insert(types.InlineKeyboardButton(text="Оставить заявку", callback_data="register"))
            await bot.send_message(callback.from_user.id, "Извините, пожалуйста, пройдите опрос снова",
                                   reply_markup=reank)
            async with state.proxy() as data:
                data['user_name'] = callback.from_user.first_name
                data['id_order'] = data['id_order']
                kb1 = types.InlineKeyboardMarkup()
                kb1.insert(types.InlineKeyboardButton(text="Оставить заявку", callback_data="register"))

        time.sleep(1)
        await main_menu(callback)
        await state.finish()

