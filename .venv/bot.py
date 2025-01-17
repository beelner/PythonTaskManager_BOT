from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import asyncio
import json
import os

# Токен и инициализация
API_TOKEN = "7691260198:AAEGzqqiAJjUqNwBf440cwe9DxkdzcPcYXI"
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def check_file_exists():
    if not os.path.exists("tasks.json"):
        with open("tasks.json", "w") as file:
            json.dump({}, file, indent=4)


def load_tasks():
    check_file_exists()
    try:
        with open("tasks.json", "r") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def save_tasks():
    with open("tasks.json", "w") as file:
        json.dump(user_tasks, file, indent=4)


# Словарь для задач
user_tasks = {}

# Определяем состояния
class TaskStates(StatesGroup):
    waiting_for_task = State()
    waiting_for_task_number = State()

# Создаем завуалированную клавиатуру
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить задачу"), KeyboardButton(text="Список задач")],
        [KeyboardButton(text="Удалить задачу"), KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True  # Клавиатура будет компактной
)

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    global user_tasks
    user_tasks = load_tasks()
    await message.reply(
        "Привет! 👋\n"
        "Я твой Task Manager Бот. Используй кнопки ниже для управления задачами.",
        reply_markup=main_menu
    )

# Завуалированное добавление задачи
@dp.message(lambda msg: msg.text == "Добавить задачу")
async def add_command(message: Message, state: FSMContext):
    await message.reply("Введите текст задачи:")
    await state.set_state(TaskStates.waiting_for_task)

@dp.message(TaskStates.waiting_for_task)
async def process_task_text(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    task = message.text.strip()
    if not task:
        await message.reply("Текст задачи не может быть пустым!")
        return
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append(task)
    save_tasks()
    await message.reply(f"Задача '{task}' добавлена!", reply_markup=main_menu)
    await state.clear()

# Завуалированный список задач
@dp.message(lambda msg: msg.text == "Список задач")
async def list_command(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in user_tasks or not user_tasks[user_id]:
        await message.reply("У вас пока нет задач.")
    else:
        tasks = "\n".join([f"📌 {i + 1}. {task}" for i, task in enumerate(user_tasks[user_id])])
        await message.reply(f"Ваши задачи:\n{tasks}")

#Обработка команды "помощь"
@dp.message(lambda msg: msg.text == "Помощь")
async def help_command(message: Message):
    await message.reply(
        "Используйте кнопки ниже для управления задачами:\n"
        "1 Добавить задачу\n"
        "2 Список задач\n"
        "3 Удалить задачу\n"
        "4 Помощь"
    )

# Завуалированное удаление задачи
@dp.message(lambda msg: msg.text == "Удалить задачу")
async def delete_command(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id not in user_tasks or not user_tasks[user_id]:
        await message.reply("У вас нет задач для удаления.")
        return
    tasks = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(user_tasks[user_id])])
    await message.reply(f"Ваши задачи:\n{tasks}\n\nВведите номер задачи для удаления:")
    await state.set_state(TaskStates.waiting_for_task_number)

@dp.message(TaskStates.waiting_for_task_number)
async def process_task_number(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    try:
        task_number = int(message.text) - 1
        if task_number < 0 or task_number >= len(user_tasks[user_id]):
            raise ValueError
        removed_task = user_tasks[user_id].pop(task_number)
        await message.reply(f"Задача '{removed_task}' удалена!", reply_markup=main_menu)
        save_tasks()
        await state.clear()
    except (ValueError, IndexError):
        await message.reply("Некорректный номер задачи. Попробуйте снова.")


@dp.message()
async def echo(message: Message):
    print(f"[{datetime.now()}] Сообщение от {message.from_user.full_name} (ID: {message.from_user.id}): {message.text}")


# Запуск бота
async def main():
    global user_tasks
    user_tasks = load_tasks()
    dp.message.register(start_command, Command("start"))
    dp.message.register(add_command, lambda msg: msg.text == "Добавить задачу")
    dp.message.register(list_command, lambda msg: msg.text == "Список задач")
    dp.message.register(delete_command, lambda msg: msg.text == "Удалить задачу")
    dp.message.register(process_task_text, TaskStates.waiting_for_task)
    dp.message.register(process_task_number, TaskStates.waiting_for_task_number)
    dp.message.register(echo)

    print("Бот запущен!")
    print(f"Loaded tasks: {user_tasks}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())