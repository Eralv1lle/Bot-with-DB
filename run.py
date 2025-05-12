from aiogram import Bot, Dispatcher
import asyncio
from os import getenv
from dotenv import load_dotenv
import logging

from app.handlers import router

load_dotenv()
BOT_TOKEN = getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try: asyncio.run(main())
    except KeyboardInterrupt: print('stop')