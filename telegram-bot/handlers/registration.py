from aiogram import types, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

registration_router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_code = State()


@registration_router.message(CommandStart())
async def start_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    await message.answer("Hello, give your email for registration")

    await state.set_state(RegistrationStates.waiting_for_email)
    logger.info(f"User {user_id} ({user_name}) started registration")


@registration_router.message(RegistrationStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    user_id = message.from_user.id

    logger.info(f"User {user_id} provided email: {email}")

    # Отправить запрос к бэкенду POST /auth/register

    await message.answer(f"Код отправлен на {email}. Введи код из письма:")

    await state.update_data(email=email)

    await state.set_state(RegistrationStates.waiting_for_code)


@registration_router.message(RegistrationStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text
    user_id = message.from_user.id

    data = await state.get_data()
    email = data.get('email')

    logger.info(f"User {user_id} entered code: {code}")

    # response = await api_client.verify(user_id, code)

    await message.answer("✅ Верификация успешна! Теперь настрой город командой /settings")

    await state.clear()