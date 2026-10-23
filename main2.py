import os
import asyncio
from threading import Thread
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI
import uvicorn

# --- Конфигурация ---
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8000))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не задан!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Расписание (как у тебя было) ---
SCHEDULE = {
    0: [
        ("Основы информационной компетентности", "8:30-11:20"),
        ("Право", "12:00-14:50"),
    ],
    1: [
        ("Основы Российской государственности", "8:30-11:20"),
        ("Иностранный язык", "12:00-14:50"),
    ],
    2: [
        ("Цифровые технологии и введение в искусственный интеллект", "8:30-11:20"),
    ],
    3: [
        ("История России", "8:30-11:20"),
    ],
    4: [
        ("Основы Российской государственности", "12:00-14:50"),
    ],
    5: [
        ("Безопасность жизнедеятельности СДО РАНХиГС", None),
    ],
}

DAY_NAMES = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]

def get_schedule_for_date(date_str: str) -> str | None:
    """Возвращает расписание на день или None, если формат неверен."""
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None

    weekday = dt.weekday()  # 0=понедельник, 6=воскресенье
    if weekday == 6:
        return "В воскресенье занятий нет."

    day_name = DAY_NAMES[weekday]
    pairs = SCHEDULE.get(weekday, [])

    if not pairs:
        return f"{day_name}:\nНет занятий."

    lines = [f"{day_name}:"]
    for subject, time_range in pairs:
        if time_range:
            lines.append(f"{subject} {time_range}")
        else:
            lines.append(subject)

    return "\n".join(lines)

# --- Обработчики бота (aiogram) ---
@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()
    # Пытаемся распарсить дату
    response = get_schedule_for_date(text)
    if response is not None:
        await message.answer(response)
    else:
        # Если это не дата — можно дать подсказку
        await message.answer("Пожалуйста, отправь дату в формате ДД.ММ.ГГГГ (например, 23.10.2024), чтобы получить расписание.")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне дату в формате ДД.ММ.ГГГГ, и я пришлю расписание на этот день.")

# --- HTTP часть (для Render) ---
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "service": "telegram-schedule-bot"}

@app.get("/")
def root():
    return {"message": "Бот работает. Эндпоинт /health для проверки статуса."}

# Функция, которая запускает polling в отдельном потоке
def run_polling():
    asyncio.run(dp.start_polling(bot))

# Запуск
if __name__ == "__main__":
    # Запускаем polling в отдельном потоке, чтобы не блокировать HTTP-сервер
    t = Thread(target=run_polling, daemon=True)
    t.start()

    # Запускаем HTTP-сервер (его и будет проверять Render)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
