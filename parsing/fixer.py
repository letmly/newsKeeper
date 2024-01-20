import os
import shutil
import json

# Путь к директории с файлами
source_directory = 'news_texts1'

# Путь к JSON-файлу
json_file_path = 'facts_ref.json'

# Путь к директории, в которую будут скопированы файлы
destination_directory = 'remaining_texts22'
os.makedirs(destination_directory, exist_ok=True)
json_ids = []


# Чтение JSON-файла
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    # Попробуем загрузить данные с учетом дополнительных квадратных скобок
    json_data = json.loads(json.dumps([json.loads(x) for x in json_file.read().split('][')]))
    # json_data = json.loads(json_file.read().replace('][', ','))
    # file_names = json_data.get("Url", "").replace("\\", "")

    # Проход по каждой записи в JSON-данных
    for entry in json_data:
        # Извлечение значения "Url" (имени файла) из записи
        json_ids.append(entry.get("Url", "").replace("\\", "").replace(".txt", ""))

# Извлечение идентификаторов из JSON
# json_ids = {os.path.splitext(entry["Url"])[0][1:]: True for entry in json_data}

# Проход по файлам в исходной директории
for filename in os.listdir(source_directory):
    file_id, file_extension = os.path.splitext(filename)
    if file_id not in json_ids:
        source_path = os.path.join(source_directory, filename)
        destination_path = os.path.join(destination_directory, filename)
        shutil.copyfile(source_path, destination_path)
        print(f"Файл {filename} скопирован.")

print("Копирование завершено.")
