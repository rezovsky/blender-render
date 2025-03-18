# routers/folder_tree.py
import os
import time
import hashlib
import threading
from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
from typing import List, Dict, Union, Optional

from modules.db import SessionLocal  # или ваш способ получения сессии
from sqlalchemy.orm import Session

from utils.path_utils import split_path_to_json, join_path_from_json
from models.folder_cache import FolderCache

router = APIRouter()


# --------- Утилита для хеширования пути+маски ---------
def hash_path(path: str, mask: Optional[str] = None) -> str:
    """Создает MD5-хеш от пути + маски (если маска есть)."""
    base = path
    if mask:
        base += f"::{mask}"
    return hashlib.md5(base.encode()).hexdigest()

# --------- Рекурсивная функция сканирования папки ---------
def get_folder_structure(path: Path, mask: Optional[str] = None) -> List[Dict[str, Union[str, List]]]:
    """
    Рекурсивно собираем дерево папок и файлы по маске (если указана).
    Возвращает список элементов, где у каждой папки есть children.
    """
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid folder path")

    items = []
    dirs = filter(lambda p: p.is_dir(), path.iterdir())

    # Сканы папок:
    for item in sorted(dirs, key=lambda x: x.name.lower()):
        node = {
            "id": hash_path(str(item), mask),
            "value": os.path.normpath(str(item)),  # Для фронта — строка пути
            "path_encoded": split_path_to_json(str(item)),  # Массив для БД
            "label": item.name,
            # Рекурсивно для подпапок
            "children": get_folder_structure(item, mask)
        }
        items.append(node)

    # Если указана маска — нужно получить файлы с определённым расширением
    if mask:
        ext = mask.lstrip("*").lower()  # убираем '*' в начале, если пользователь ввёл '*.blend'
        files = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() == f".{ext}"]
        for file in sorted(files, key=lambda x: x.name.lower()):
            file_node = {
                "id": hash_path(str(file), mask),
                "value": os.path.normpath(str(file)),
                "path_encoded": split_path_to_json(str(file)),
                "label": file.name
            }
            items.append(file_node)

    return items

# --------- Получение или создание структуры папок в БД ---------
def get_or_create_folder_structure(db: Session, path: Path, mask: Optional[str]) -> List[Dict[str, Union[str, List]]]:
    """
    Пытается найти структуру по path+mask в БД.
    Если нет — сканирует файловую систему, сохраняет в БД, возвращает.
    """
    path_str = str(path)
    path_hash_value = hash_path(path_str, mask)

    # Ищем запись по хешу:
    cache_item = db.query(FolderCache).filter(FolderCache.path_hash == path_hash_value).first()

    if cache_item:
        # Если нашли — возвращаем её
        return cache_item.data
    else:
        # Если нет — сканируем и сохраняем
        tree_data = get_folder_structure(path, mask)

        new_cache_item = FolderCache(
            path_hash=path_hash_value,
            path=split_path_to_json(path_str),
            mask=mask,
            data=tree_data
        )
        db.add(new_cache_item)
        db.commit()
        db.refresh(new_cache_item)

        return tree_data

# --------- Роут для получения дерева папок ---------
@router.get("/browser_tree")
def folder_tree(
    path: str = Query(..., title="Folder Path"),
    mask: Optional[str] = Query(None, title="File Mask", description="Фильтрация по расширению (например, '*.blend' или 'blend')")
):
    """
    Возвращает дерево папок и файлов, учитывая маску (если она задана).
    При первом запросе с данным path+mask сканирует и сохраняет в БД, дальше — выдаёт из кэша.
    """
    folder_path = Path(path)
    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    with SessionLocal() as db:
        tree_data = get_or_create_folder_structure(db, folder_path, mask)
    return tree_data

# --------- Фоновый процесс циклического сканирования ---------
def cyclical_scanning():
    """
    Фоновая задача, которая в бесконечном цикле:
      1. Берёт все записи из folder_cache (path + mask).
      2. Сканирует заново (get_folder_structure).
      3. Обновляет запись в БД.
      4. Повторяет.
    """
    while True:
        try:
            with SessionLocal() as db:
                # Достаём все пути из кэша
                all_cache_items = db.query(FolderCache).all()

                for item in all_cache_items:
                    folder_path_str = join_path_from_json(item.path)
                    folder_path = Path(folder_path_str)

                    # Проверяем, что папка существует
                    if folder_path.exists() and folder_path.is_dir():
                        # Сканируем заново
                        tree_data = get_folder_structure(folder_path, item.mask)
                        # Обновляем запись
                        item.data = tree_data
                        db.commit()

            # Небольшая пауза между итерациями, чтобы не крутиться бесконечно на 100% CPU
            time.sleep(10)

        except Exception as e:
            # Логируем ошибку (или print для примера)
            print(f"[cyclical_scanning] Ошибка: {e}")
            time.sleep(5)

# --------- Глобальная переменная для хранения ссылки на процесс сканирования ---------
scanner_process = None

@router.post("/start_cyclical_scan")
def start_cyclical_scan():
    global scanner_process

    if scanner_process is not None and scanner_process.is_alive():
        return {"status": "Сканирование уже запущено"}

    scanner_process = threading.Thread(target=cyclical_scanning, daemon=True)
    scanner_process.start()

    return {"status": "Сканирование запущено"}
