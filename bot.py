import datetime
import logging
import asyncio
import time
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from apscheduler.schedulers.background import BackgroundScheduler
import os

# --- НАСТРОЙКИ ---
TOKEN = '8069252349:AAEGXgG0KH9Ybzq6A34DX91MaHNIcMm7_y0'

MY_ID = 661326630          # ← Telegram ID
HER_ID = 1175351775         # ← ID девушки
PHRASES_FILE = "phrases.txt"
PHOTOS_FOLDER = "photos"

# --- ЛОГИ ---
logging.basicConfig(level=logging.INFO)

# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
scheduler = BackgroundScheduler()

# --- ОТПРАВКА СООБЩЕНИЯ ---
async def send_message(chat_id):
    day_number = datetime.datetime.now().timetuple().tm_yday
    logging.info(f"День #{day_number} - отправка в chat_id: {chat_id}")

    try:
        with open(PHRASES_FILE, "r", encoding="utf-8") as f:
            phrases = f.readlines()

        if day_number > len(phrases):
            logging.warning("Фраз больше нет!")
            return

        phrase = phrases[day_number - 1].strip()
        photo_path = os.path.join(PHOTOS_FOLDER, f"{day_number}.jpg")

        if not os.path.isfile(photo_path):
            logging.warning(f"Фото не найдено: {photo_path}")
            await bot.send_message(chat_id=chat_id, text=phrase)
            return

        photo = FSInputFile(photo_path)
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=phrase)
        logging.info(f"Отправлено в chat_id {chat_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке: {e}")

# Обёртка для запуска из планировщика
def send_to_me():
    asyncio.run(send_message(MY_ID))

def send_to_her():
    asyncio.run(send_message(HER_ID))

# --- РАСПИСАНИЕ ---
scheduler.add_job(send_to_me, "cron", hour=8, minute=45)
scheduler.add_job(send_to_her, "cron", hour=9, minute=0)

# --- ЗАПУСК ---
if __name__ == '__main__':
    asyncio.run(send_message(MY_ID))  # тестовая отправка при запуске
    logging.info("Бот запущен, ждёт времени отправки...")
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Бот остановлен.")

