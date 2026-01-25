import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv

#from handlers.search import search_router


load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

dp = Dispatcher()


# dp.include_router(search_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())