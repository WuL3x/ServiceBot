from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

# Главное меню
button_menu = InlineKeyboardButton('Меню')
button_help = InlineKeyboardButton('Техническая поддержка')
button_reg = InlineKeyboardButton('Заявка на ремонт')

bt_sec = ReplyKeyboardMarkup(resize_keyboard=True).add(button_menu).row(button_help).row(button_reg)

kb_dev = InlineKeyboardMarkup()
kb_dev.insert(InlineKeyboardButton(text="Планшет", callback_data='device:Планшет'))
kb_dev.add(InlineKeyboardButton(text="Смартфон", callback_data='device:Смартфон'))
kb_dev.add(InlineKeyboardButton(text="Компьютер", callback_data='device:Компьютер'))
