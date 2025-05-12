from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import sqlite3

from app.keyboard import create_markup


router = Router()

class Registration(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


@router.message(CommandStart())
async def start_message(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute("""CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL)""")
    cr.execute(f"""SELECT * FROM Users WHERE id = {message.from_user.id}""")
    if cr.fetchall():
        await message.answer('Вы уже есть в БД. Можете удалить или изменить данные', reply_markup=create_markup(['Удалить аккаунт', 'Изменить данные']))
    else:
        await message.answer('Приветствую. Здесь вы можете зарегистрироваться в БД', reply_markup=create_markup(['Зарегистрироваться в БД']))

    con.commit()
    con.close()


@router.message(F.text == 'Зарегистрироваться в БД')
async def start_reg(message: Message, state: FSMContext):
    await message.answer('Отлично! Пожалуйста введите ваш логин: ')
    await state.set_state(Registration.waiting_for_login)


@router.message(Registration.waiting_for_login)
async def get_name(message: Message, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()
    cr.execute(f"SELECT * FROM Users WHERE login = '{message.text}'")
    if not cr.fetchall():
        await state.update_data(login=message.text)
        await state.set_state(Registration.waiting_for_password)
        await message.answer('Отлично! Теперь введите пароль: ')
    else:
        await message.answer('Такой пользователь уже существует. Пожалуйста, введите другой логин: ')

    con.commit()
    con.close()


@router.message(Registration.waiting_for_password)
async def get_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    con = sqlite3.connect('data.db')

    cr = con.cursor()
    cr.execute(f"INSERT INTO Users VALUES ({int(message.from_user.id)}, '{data['login']}', '{data['password']}')")

    con.commit()
    con.close()

    await message.answer('Отлично! Регистрация завершена')
    await state.clear()