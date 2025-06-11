import datetime
import logging
import asyncio
import pytz
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from apscheduler.schedulers.background import BackgroundScheduler
from aiohttp import web

# === НАСТРОЙКИ ===
TOKEN = "8069252349:AAEGXgG0KH9Ybzq6A34DX91MaHNIcMm7_y0"
MY_ID = 661326630         # ← Твой Telegram ID
HER_ID = 1175351775       # ← ID девушки
PHRASES_FILE = "phrases.txt"
PHOTOS_FOLDER = "photos"

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === ИНИЦИАЛИЗАЦИЯ БОТА ===
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# === ОТПРАВКА СООБЩЕНИЯ ===
async def send_message(chat_id):
    day_number = datetime.datetime.now().timetuple().tm_yday
    logging.info(f"День #{day_number} - отправка в chat_id: {chat_id}")

    try:
        with open(PHRASES_FILE, "r", encoding="utf-8") as f:
            phrases = f.readlines()

        if day_number > len(phrases):
            await bot.send_message(chat_id, "Фразы закончились 😢")
            return

        phrase = phrases[day_number - 1].strip()
        photo_path = f"{PHOTOS_FOLDER}/{day_number}.jpg"

        photo = FSInputFile(photo_path)
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=phrase)

        logging.info(f"Отправлено в chat_id {chat_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке: {e}")

# === ПЛАНИРОВЩИК ===
scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Moscow"))

# Тебе в 8:45
scheduler.add_job(lambda: asyncio.run(send_message(MY_ID)), "cron", hour=8, minute=45)

# Девушке в 9:00
scheduler.add_job(lambda: asyncio.run(send_message(HER_ID)), "cron", hour=9, minute=0)

# === aiohttp сервер для Render ===
async def handle(request):
    return web.Response(text="Bot is running")

async def run_web():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port=8080)
    await site.start()

# === Главная асинхронная функция запуска ===
async def main():
    await run_web()
    scheduler.start()  # Запускаем планировщик тут
    await send_message(MY_ID)  # Тестовое сообщение при старте
    logging.info("Бот запущен")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
