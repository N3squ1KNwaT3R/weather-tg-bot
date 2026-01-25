import asyncio
import os
from loguru import logger
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.registration import registration_router

load_dotenv(find_dotenv())

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def main():

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(registration_router)
    try:
        logger.info("Starting Telegram Bot...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())