import json
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ВСТАВЬТЕ ВАШ ТОКЕН
API_TOKEN = '8253785216:AAFBkQq1iKFGckU5fiaM9x_LkTvxAqeynwI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для перевода английских дней недели в русские (как на сайте)
DAYS_TRANSLATE = {
    "Monday": "понедельник",
    "Tuesday": "вторник",
    "Wednesday": "среда",
    "Thursday": "четверг",
    "Friday": "пятница",
    "Saturday": "суббота",
    "Sunday": "воскресенье"
}

def get_lessons_by_day_name(day_name_ru):
    try:
        with open('schedule.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ищем все занятия, где день недели совпадает (например, "вторник")
        # Мы берем только уникальные занятия для этого дня недели, 
        # чтобы избежать дублей, если вы скачали несколько недель.
        day_lessons = []
        seen_items = set()

        for item in data:
            if item['День'].lower() == day_name_ru.lower():
                # Создаем уникальный ключ (время + предмет), чтобы не повторяться
                fingerprint = f"{item['Время']}{item['Предмет']}"
                if fingerprint not in seen_items:
                    day_lessons.append(item)
                    seen_items.add(fingerprint)
        
        if not day_lessons:
            return f"📅 {day_name_ru.capitalize()}\nЗанятий не найдено."

        # Сортируем по времени (на всякий случай)
        day_lessons.sort(key=lambda x: x['Время'])

        res = f"📅 Расписание на {day_name_ru.upper()} (Зациклено):\n\n"
        for l in day_lessons:
            res += f"⏰ {l['Время']} - {l['Предмет']}\n"
            res += f"📍 {l['Аудитория']} ({l['Тип']})\n"
            res += f"👨‍🏫 {l['Преподаватель']}\n"
            res += "----------------------------\n"
        return res
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"

# Кнопки
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Сегодня")
    builder.button(text="Завтра")
    builder.button(text="Выбрать день")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def days_menu():
    builder = ReplyKeyboardBuilder()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    for day in days:
        builder.button(text=day)
    builder.button(text="⬅️ Назад")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот запущен. Расписание зациклено по дням недели.", reply_markup=main_menu())

@dp.message(lambda message: message.text == "Сегодня")
async def today(message: types.Message):
    # Узнаем какой сегодня день недели на английском
    today_en = datetime.now().strftime("%A")
    # Переводим на русский
    today_ru = DAYS_TRANSLATE.get(today_en, "понедельник")
    text = get_lessons_by_day_name(today_ru)
    await message.answer(text)

@dp.message(lambda message: message.text == "Завтра")
async def tomorrow(message: types.Message):
    # Узнаем какой день будет завтра
    tomorrow_en = (datetime.now() + timedelta(days=1)).strftime("%A")
    tomorrow_ru = DAYS_TRANSLATE.get(tomorrow_en, "понедельник")
    text = get_lessons_by_day_name(tomorrow_ru)
    await message.answer(text)

@dp.message(lambda message: message.text == "Выбрать день")
async def show_days(message: types.Message):
    await message.answer("Выберите день недели:", reply_markup=days_menu())

@dp.message(lambda message: message.text == "⬅️ Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu())

@dp.message(lambda message: message.text in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"])
async def show_by_name(message: types.Message):
    text = get_lessons_by_day_name(message.text)
    await message.answer(text)

async def main():
    while True: # Бесконечный цикл для перезапуска бота при сбоях сети
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Сбой сети: {e}. Повтор через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())