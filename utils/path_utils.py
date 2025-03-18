import os
import json

def split_path_to_json(path: str | None) -> str | None:
    """Разбиваем путь на массив и сохраняем как JSON."""
    if not path:
        return None
    separator = "\\" if "\\" in path else "/"
    return json.dumps(path.split(separator))  # Храним путь как JSON-строку

def join_path_from_json(path_json: str | None) -> str | None:
    """Собираем путь обратно из JSON, фиксируем отсутствие слэша после буквы диска."""
    if not path_json:
        return None
    path_list = json.loads(path_json)  # Десериализуем JSON

    if not path_list:
        return None

    path = os.path.join(*path_list)  # Собираем путь

    # 🔥 Фикс для Windows: добавляем `/` после `Z:`
    if os.name == "nt" and len(path_list[0]) == 2 and path_list[0][1] == ":":
        path = path_list[0] + "/" + "/".join(path_list[1:])

    return path
