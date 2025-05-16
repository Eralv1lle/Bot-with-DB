from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import sqlite3
from pprint import pprint

from app.keyboard import edit_kb, in_db, not_in_db, show_pass, hide_pass


router = Router()

class Registration(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

class EditInfo(StatesGroup):
    editing_login = State()
    editing_password = State()


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
        await message.answer('Вы уже есть в БД ✅. Можете удалить или изменить данные', reply_markup=in_db)
    else:
        await message.answer('Приветствую. Здесь вы можете зарегистрироваться в БД', reply_markup=not_in_db)

    con.commit()
    con.close()


@router.message(F.text == 'Зарегистрироваться в БД')
async def start_reg(message: Message, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()
    cr.execute(f"SELECT * FROM Users WHERE id = '{message.from_user.id}'")
    if cr.fetchall():
        await message.answer('Вы уже зарегистрированы ✅')
    else:
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

    await message.answer(f'Отлично! Регистрация завершена ✅\n\nВаш логин {data['login']}\nВаш пароль: {data['password']}', reply_markup=in_db)
    await state.clear()


@router.message(F.text == 'Мой профиль')
async def check_profile(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {message.from_user.id}")
    data = cr.fetchall()
    if data:
        await message.answer(f'Ваш логин: {data[0][1]}\nВаш пароль: {'*' * len(data[0][2])}', reply_markup=show_pass)
    else:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    cr.close()

@router.callback_query(F.data == 'showpass')
async def show_password(callback: CallbackQuery):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {callback.from_user.id}")
    data = cr.fetchall()
    if data:
        await callback.answer('Показать пароль')
        await callback.message.edit_text(f'Ваш логин: {data[0][1]}\nВаш пароль: {data[0][2]}', reply_markup=hide_pass)
    else:
        await callback.answer('Вы не зарегистрированы')
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    cr.close()


@router.callback_query(F.data == 'hidepass')
async def hide_password(callback: CallbackQuery):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {callback.from_user.id}")
    data = cr.fetchall()
    if data:
        await callback.answer('Скрыть пароль')
        await callback.message.edit_text(f'Ваш логин: {data[0][1]}\nВаш пароль: {'*' * len(data[0][2])}', reply_markup=show_pass)
    else:
        await callback.answer('Вы не зарегистрированы')
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    cr.close()


@router.message(F.text == 'Удалить аккаунт')
async def del_acc(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f'SELECT *  FROM Users WHERE id = {int(message.from_user.id)}')

    if cr.fetchall():
        cr.execute(f'DELETE FROM Users WHERE id = {int(message.from_user.id)}')
        con.commit()
        con.close()
        await message.answer('Аккаунт удалён')
    else:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)


@router.message(F.text == 'Изменить данные')
async def edit_acc(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f'SELECT * FROM Users WHERE id = {message.from_user.id}')
    if not cr.fetchall():
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)
    else:
        await message.answer('Отлично! Выберите, что хотите изменить:', reply_markup=edit_kb)


@router.callback_query(F.data == 'editlogin')
async def change_login(callback: CallbackQuery, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT login FROM Users WHERE id = {callback.from_user.id}")
    if cr.fetchall():
        await callback.answer('Вы выбрали изменить логин ✅')
        await callback.message.answer('Введите новый логин:')
        await state.set_state(EditInfo.editing_login)
    else:
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)


@router.callback_query(F.data == 'editpassword')
async def change_password(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали изменить пароль ✅')
    await state.set_state(EditInfo.editing_password)


@router.message(EditInfo.editing_login)
async def edit_login(message: Message, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT login FROM Users WHERE id = {message.from_user.id}")
    data = cr.fetchall()
    if not data:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)
    elif data[0][0] == message.text:
        await message.answer('Вы ввели свой же логин, пожалуйста введите другой')
    else:
        cr.execute(f"SELECT * FROM Users WHERE login = '{message.text}'")
        if cr.fetchall():
            await message.answer('Такой пользователь уже существует. Пожалуйста, введите другой логин:', reply_markup=in_db)
        else:
            cr.execute(f"UPDATE Users SET login = '{message.text}' WHERE id = {int(message.from_user.id)}")
            await state.clear()
            await message.answer(f'Логин изменён ✅\nНовый логин: {message.text}', reply_markup=in_db)

    con.commit()
    con.close()


@router.message(Command('all'), F.from_user.id == 1999317423)
async def list_of_users(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute('SELECT * FROM Users')
    users = ''

    for i, info in enumerate(cr.fetchall(), start=1):
        user_id, login, password = info
        users += f'{i}. id = {user_id}, {login} - {password}\n'

    await message.answer(users)

    con.commit()
    con.close()


@router.message()
async def ya_blat_ne_ponimau(message: Message):
    await start_message(message)