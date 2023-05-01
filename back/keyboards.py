from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Главное меню
button_menu = InlineKeyboardButton(text='Меню', callback_data='menu')
# bt_reg = InlineKeyboardButton(text='Оставить заявку на ремонт', callback_data='register')
# bt_kons = InlineKeyboardButton(text="Техподдержка", callback_data='konsult')
bt_sec = ReplyKeyboardMarkup(resize_keyboard=True).add(button_menu)

kb1 = InlineKeyboardMarkup()
kb1.insert(InlineKeyboardButton(text="Оставить заявку на ремонт", callback_data='register'))
kb1.insert(InlineKeyboardButton(text="Техподдержка", callback_data='konsult'))
kb1.add(InlineKeyboardButton(text="Виды услуг", callback_data='katalog'))
kb1.add(InlineKeyboardButton(text="Статус заказа",
                                   web_app=WebAppInfo(url='https://wul3x.github.io/ServerBot-site')))
kb1.add(InlineKeyboardButton(text='Где мы находимся?', callback_data='place'))
kb1.add(InlineKeyboardButton(text='О компании', callback_data='company'))

bt_feed = InlineKeyboardMarkup()
bt_feed.insert(InlineKeyboardButton(text='Вопрос', callback_data='feed:Вопрос'))
bt_feed.add(InlineKeyboardButton(text='Ошибка', callback_data='feed:Ошибка'))
bt_feed.add(InlineKeyboardButton(text='Отзыв', callback_data='feed:Отзыв'))

bt_remont = InlineKeyboardButton(text='Ремонт', callback_data='remont')
bt_diag = InlineKeyboardButton(text='Диагностика', callback_data='diag')
bt_upgrade = InlineKeyboardButton(text='Апгрейд ПК', callback_data='upgrade')
bt_virus = InlineKeyboardButton(text='Удаление вирусов', callback_data='virus')
bt_tup = InlineKeyboardButton(text='Если просто не включается компьютер?', callback_data='tup')
bt_menu = InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')
bt_kat = ReplyKeyboardMarkup(resize_keyboard=True).add(bt_remont).insert(bt_virus).insert(bt_upgrade).insert(bt_diag)\
    .insert(bt_tup).add(bt_menu)

kb_dev = InlineKeyboardMarkup()
kb_dev.insert(InlineKeyboardButton(text="Планшет", callback_data='device:Планшет'))
kb_dev.add(InlineKeyboardButton(text="Смартфон", callback_data='device:Смартфон'))
kb_dev.add(InlineKeyboardButton(text="Компьютер", callback_data='device:Компьютер'))



