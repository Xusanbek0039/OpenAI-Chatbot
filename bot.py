import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import router

async def main():
    # 🔔 Konsolga log chiqarish (kim /start bosdi, kim nima yozdi va h.k.)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )

    logging.info("🤖 Bot ishga tushmoqda...")

    # Botni yaratish
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    # Dispatcher (router'lar uchun)
    dp = Dispatcher()
    dp.include_router(router)

    # Pollingni boshlash
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("❌ Bot to‘xtatildi.")
