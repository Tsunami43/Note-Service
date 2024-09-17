from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from provider import provider_user
from provider.models import AccessTokenResponse


# Создаем отдельные стейты для регистрации
class RegisterStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


# Инициализируем роутер для регистрации
router = Router()


# Обработчик команды /register (начало регистрации)
@router.message(Command("register"))
async def handler_register(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    if not user:
        await message.answer(
            "Для отмены действия /cancel.\n\nВведите логин для регистрации:"
        )
        await state.set_state(RegisterStates.waiting_for_login)
    else:
        await message.answer("Вы уже авторизованны")


# Обработчик ввода логина при регистрации
@router.message(StateFilter(RegisterStates.waiting_for_login))
async def handle_register_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await state.set_state(RegisterStates.waiting_for_password)


# Обработчик ввода пароля при регистрации
@router.message(StateFilter(RegisterStates.waiting_for_password))
async def handle_register_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get("login")
    password = message.text
    user = await provider_user.create_user(login, password, message.from_user.id)
    if not user:
        await message.answer(f"Ошибка регистрации")
    else:
        await message.answer("Вы успешно зарегистрированы!")
    await state.clear()
