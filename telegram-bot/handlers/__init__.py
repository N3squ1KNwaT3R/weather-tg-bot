from aiogram import Router
from aiogram.filters import Command
from aiogram import types

help_router = Router()

@help_router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "🤖 Доступные команды:\n\n"
        "/start - Регистрация / Профиль\n"
        "/setcity - Установить свой город\n"
        "/weather [город] - Текущая погода\n"
        "/tomorrow [город] - Прогноз на завтра\n"
        "/hourly [город] - Почасовой прогноз\n"
        "/help - Показать эту справку\n\n"
        "Примеры:\n"
        "/weather - погода в твоем городе\n"
        "/weather Warszawa - погода в Варшаве\n"
        "/tomorrow Kraków - прогноз на завтра\n"
        "/hourly - прогноз по часам"
    )