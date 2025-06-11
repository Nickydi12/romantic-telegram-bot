import datetime
import logging
import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ ---
TOKEN = '8069252349:AAEGXgG0KH9Ybzq6A34DX91MaHNIcMm7_y0'        # вставь сюда токен бота
USER_ID = 661326630             # твой Telegram ID (получишь тестовое сообщение)
GIRLFRIEND_ID = 1175351775        # ID девушки (получит основное сообщение в 9:00)
PHRASES_FILE = "phrases.txt"
PHOTOS_FOLDER = "photos"

# --- ЛОГИ ---
logging.basicConfig(level=logging.INFO)

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
scheduler = AsyncIOScheduler()

# --- Функция отправки сообщения ---
async def send_message(chat_id, day_number):
    try:
        with open(PHRASES_FILE, encoding='utf-8') as f:
            phrases = f.readlines()
        if day_number > len(phrases):
            logging.warning("Фраз больше нет!")
            return
        phrase = phrases[day_number - 1].strip()
        photo_path = f"{PHOTOS_FOLDER}/{day_number}.jpg"
        photo = FSInputFile(photo_path)
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=phrase)
        logging.info(f"Отправлено в chat_id {chat_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке в chat_id {chat_id}: {e}")

# --- Отправка тестового сообщения только тебе ---
async def send_test_message():
    try:
        await bot.send_message(chat_id=USER_ID, text="Бот успешно запущен и готов к работе!")
        logging.info("Тестовое сообщение отправлено тебе.")
    except Exception as e:
        logging.error(f"Ошибка при отправке тестового сообщения: {e}")

# --- Задачи по расписанию ---
async def job_send_to_me():
    day_number = datetime.datetime.now().timetuple().tm_yday
    logging.info(f"День #{day_number} - отправка предварительного сообщения тебе")
    await send_message(USER_ID, day_number)

async def job_send_to_girlfriend():
    day_number = datetime.datetime.now().timetuple().tm_yday
    logging.info(f"День #{day_number} - отправка сообщения девушке")
    await send_message(GIRLFRIEND_ID, day_number)

# --- Главный блок запуска ---
if __name__ == '__main__':
    async def main():
        await send_test_message()  # тестовое сообщение при старте (только тебе)
        scheduler.add_job(job_send_to_me, 'cron', hour=8, minute=45)
        scheduler.add_job(job_send_to_girlfriend, 'cron', hour=9, minute=0)
        scheduler.start()
        logging.info("Бот запущен, ждёт времени отправки...")
        while True:
            await asyncio.sleep(3600)

    asyncio.run(main())
