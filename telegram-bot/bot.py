import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from handlers.registration import registration_router
from handlers.settings import settings_router
from handlers.weather import weather_router

from handlers import help_router


async def main():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(registration_router)
    dp.include_router(settings_router)
    dp.include_router(weather_router)
    dp.include_router(help_router)

    logger.info("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
