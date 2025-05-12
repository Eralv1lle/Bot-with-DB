from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_markup(buttons):
    markup = ReplyKeyboardBuilder()
    for btn in buttons:
        markup.add(KeyboardButton(text=btn))
    return markup.adjust(2).as_markup(resize_keyboard=True)

edit_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Логин', callback_data='editlogin'), InlineKeyboardButton(text='Пароль', callback_data='editpassword')]
])

in_db = create_markup(['Удалить аккаунт', 'Изменить данные'])
not_in_db = create_markup(['Зарегистрироваться в БД'])