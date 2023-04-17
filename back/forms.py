import uuid

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import callback_data

from config import CHANNEL_ID

from back.keyboards import bt_sec, kb_dev
from main import bot, dp

button_cancel = types.InlineKeyboardButton('Отмена', callback_data='cancel')
cancelButton = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)


def register():
    class RepairForm(StatesGroup):
        id_order = State()
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

        await state.finish()
        await bot.send_message(message.from_user.id, text='''Отмена отправки⛔''', reply_markup=bt_sec)

    @dp.callback_query_handler(lambda c: c.data == 'register', state="*")
    async def register_order(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.send_message(callback_query.from_user.id,
                               f'{callback_query.from_user.first_name}, Укажите тип и название устройства.',
                               reply_markup=cancelButton)
        await bot.send_message(callback_query.from_user.id, 'Выберите тип устройства:', reply_markup=kb_dev)
        await RepairForm.id_order.set()

    @dp.callback_query_handler(state=RepairForm.id_order)
    async def process_id(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['user_name'] = callback.from_user.first_name
            data['id_order'] = str(uuid.uuid4().int)[:6]
        await RepairForm.device.set()


    @dp.callback_query_handler(lambda c: c.data.startswith('device:'), state=RepairForm.device)
    async def process_device(callback: types.CallbackQuery, state: FSMContext):
        data = callback.data.split(':')
        device = data[1]

        # сохраняем данные в состоянии
        await state.update_data(device=device)

        await bot.send_message(callback.from_user.id, "Пожалуйста, напишите полное название устройства. Если это ПК, то укажите ПК.",
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
            text = f"Заявка на ремонт устройства {data['device']}:\n"
            text += f"Номер заявки: {data['id_order']}\n"
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
            await bot.send_message(callback.from_user.id, "Спасибо за заявку!")
            async with state.proxy() as data:
                text = f"Заявка на ремонт устройства {data['device']}:\n"
                text += f"@{data['user_name']}\n"
                text += f"Номер заявки: {data['id_order']}\n"
                text += f"Название устройства: {data['dev_name']}\n"
                text += f"Описание проблемы: {data['issue']}\n"
                text += f"Имя: {data['name']}\n"
                text += f"Телефон: {data['phone']}\n"
            await bot.send_message(CHANNEL_ID, text)

        elif callback.data.split(':')[1] == 'error':
            await bot.send_message(callback.from_user.id, "Извините, пожалуйста, введите данные еще раз.")
        await state.finish()
