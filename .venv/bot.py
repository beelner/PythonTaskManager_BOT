from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import BaseMiddleware
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime

API_TOKEN = "7691260198:AAEGzqqiAJjUqNwBf440cwe9DxkdzcPcYXI"
user_tasks = {}
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

test333 = "github"



class TaskStates(StatesGroup):
    waiting_for_task = State()
    waiting_for_task_number = State()



@dp.errors()
async def global_error_handler(update, exception):
    print(f"Ошибка: {exception}")
    if isinstance(exception, TelegramAPIError):
        print("Произошла ошибка Telegram API")
    return True  # Продолжить обработку

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            user_id = event.from_user.id
            user_name = event.from_user.full_name
            message_text = event.text
            print(f"[{datetime.now()}] Сообщение от {user_name} (ID: {user_id}): {message_text}")
        return await handler(event, data)


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply(
        "Привет! 👋\n"
        "Я твой Task Manager Бот. Вот что я умею:\n"
        "1️⃣ /add - Добавить новую задачу.\n"
        "2️⃣ /list - Показать список твоих задач.\n"
        "3️⃣ /delete - Удалить задачу.\n"
        "4️⃣ /help - Подсказка по командам.\n\n"
        "Начнем планировать?"
    )

@dp.message(Command("list"))
async def list_command(message: Message):
    user_id = message.from_user.id
    if user_id not in user_tasks or not user_tasks[user_id]:
        await message.reply("У вас пока нет задач.")
    else:
        tasks = "\n".join([f"📌 {i + 1}. {task}" for i, task in enumerate(user_tasks[user_id])])
        await message.reply(f"Ваши задачи:\n{tasks}")

@dp.message(Command("add"))
async def add_command(message: Message, state: FSMContext):
    await message.reply("Введите текст задачи:")
    await state.set_state(TaskStates.waiting_for_task)

@dp.message(TaskStates.waiting_for_task)
async def process_task_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text.strip()
    if not task:
        await message.reply("Текст задачи не может быть пустым!")
        return
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append(task)
    await message.reply(f"Задача '{task}' добавлена!")
    await state.clear()

@dp.message(Command("delete"))
async def delete_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_tasks or not user_tasks[user_id]:
        await message.reply("У вас нет задач для удаления.")
        return
    tasks = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(user_tasks[user_id])])
    await message.reply(f"Ваши задачи:\n{tasks}\n\nВведите номер задачи для удаления:")
    await state.set_state(TaskStates.waiting_for_task_number)

@dp.message(TaskStates.waiting_for_task_number)
async def process_task_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        task_number = int(message.text) - 1
        if task_number < 0 or task_number >= len(user_tasks[user_id]):
            raise ValueError
        removed_task = user_tasks[user_id].pop(task_number)
        await message.reply(f"Задача '{removed_task}' удалена!")
        await state.clear()
    except (ValueError, IndexError):
        await message.reply("Некорректный номер задачи. Попробуйте снова.")

async def main():
    dp.update.middleware(LoggingMiddleware())
    dp.message.register(start_command, Command("start"))
    dp.message.register(list_command, Command("list"))
    dp.message.register(add_command, Command("add"))
    dp.message.register(delete_command, Command("delete"))
    dp.message.register(process_task_text, TaskStates.waiting_for_task)
    dp.message.register(process_task_number, TaskStates.waiting_for_task_number)

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())