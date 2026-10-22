import asyncio
import aiogram
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

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

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_schedule_for_date(date_str: str) -> str | None:

    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None

    weekday = dt.weekday()  # 0=понедельник, 6=воскресенье
    if weekday == 6:
        return "В воскресенье занятий нет."

    day_name = DAY_NAMES[weekday]
    pairs = SCHEDULE.get(weekday, )

    if not pairs:
        return f"{day_name}:\nНет занятий."

    lines = [f"{day_name}:"]
    for subject, time_range in pairs:
        if time_range:
            lines.append(f"{subject} {time_range}")
        else:
            lines.append(subject)

    return "\n".join(lines)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Отправь мне дату в формате ДД.ММ.ГГГГ, и я пришлю расписание на этот день."
    )

@dp.message()
async def handle_date(message: types.Message):
    text = message.text.strip()
    response = get_schedule_for_date(text)

    if response is None:
        await message.answer(
            "Неверный формат даты. Пожалуйста, используй формат ДД.ММ.ГГГГ (например, 23.10.2024)."
        )
        return

    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
