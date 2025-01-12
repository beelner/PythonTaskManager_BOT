import json

# Создаем список задач
task_data = []
task_name = ["task1", "task2", "task3"]
task_text = ["test1", "test2", "test3"]


# Заполняем список задач
for i in range(len(task_name)):
    task = {"name": task_name[i], "text": task_text[i]}
    task_data.append(task)


# Сохраняем данные в JSON-файл
with open("data.json", "w") as file:
    json.dump(task_data, file, indent=4)  # Сохраняем список задач в JSON-файл

# Читаем данные из JSON-файла
with open("data.json", "r") as file:
    data = json.load(file)  # Читаем данные обратно в Python-объект

# Выводим прочитанные данные
print(data)