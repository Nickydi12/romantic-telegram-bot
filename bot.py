import datetime
import logging
import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from apscheduler.schedulers.background import BackgroundScheduler

# --- НАСТРОЙКИ ---
TOKEN = '8069252349:AAEGXgG0KH9Ybzq6A34DX91MaHNIcMm7_y0'  # ← вставь токен своего бота
USER_ID = 1175351775         # ← вставь свой Telegram ID
PHRASES_FILE = "phrases.txt"
PHOTOS_FOLDER = "photos"

# --- ЛОГИ ---
logging.basicConfig(level=logging.INFO)

# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
scheduler = BackgroundScheduler()

# --- ОТПРАВКА СООБЩЕНИЯ ---
async def send_daily_message():
    day_number = datetime.datetime.now().timetuple().tm_yday
    logging.info(f"День #{day_number}")

    try:
        with open(PHRASES_FILE, "r", encoding="utf-8") as f:
            phrases = f.readlines()

        if day_number > len(phrases):
            logging.warning("Фраз больше нет!")
            return

        phrase = phrases[day_number - 1].strip()
        photo_path = f"{PHOTOS_FOLDER}/{day_number}.jpg"

        photo = FSInputFile(photo_path)
        await bot.send_photo(chat_id=USER_ID, photo=photo, caption=phrase)

        logging.info("Отправлено успешно.")
    except Exception as e:
        logging.error(f"Ошибка при отправке: {e}")

# --- РАСПИСАНИЕ ---
scheduler.add_job(lambda: asyncio.run(send_daily_message()), "cron", hour=10, minute=10)

# --- ЗАПУСК ---
if __name__ == '__main__':
    # asyncio.run(send_daily_message())  # тестовая отправка при запуске
    logging.info("Бот запущен, ждёт времени отправки...")
    scheduler.start()

    try:
        while True:
            pass  # удерживаем скрипт в активном состоянии
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Бот остановлен.")
