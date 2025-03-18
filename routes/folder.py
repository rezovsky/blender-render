import os
import hashlib
from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
from typing import List, Dict, Union, Optional
from pydantic import BaseModel
from utils.path_utils import split_path_to_json

class CreateFolderRequest(BaseModel):
    path: str

router = APIRouter()

def hash_path(path: str) -> str:
    """Создает хеш от пути, чтобы использовать его как уникальный идентификатор."""
    return hashlib.md5(path.encode()).hexdigest()

def get_folder_structure(path: Path, mask: Optional[str] = None) -> List[Dict[str, Union[str, List]]]:
    """Рекурсивно собираем дерево папок и файлов."""
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid folder path")

    items = []
    dirs = filter(lambda p: p.is_dir(), path.iterdir())

    # Сканируем подпапки
    for item in sorted(dirs, key=lambda x: x.name.lower()):
        node = {
            "id": hash_path(str(item)),  
            "value": os.path.normpath(str(item)),  
            "path_encoded": split_path_to_json(str(item)),  
            "label": item.name,
            # Рекурсия для вложенных папок
            "children": get_folder_structure(item, mask)  
        }
        items.append(node)

    # Если задана маска, добавляем соответствующие файлы
    if mask:
        ext = mask.lstrip("*").lower()
        files = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() == f".{ext}"]
        for file in sorted(files, key=lambda x: x.name.lower()):
            file_node = {
                "id": hash_path(str(file)),  
                "value": os.path.normpath(str(file)),  
                "path_encoded": split_path_to_json(str(file)),  
                "label": file.name  
            }
            items.append(file_node)

    return items

@router.get("/folder_tree")
def folder_tree(
    path: str = Query(..., title="Folder Path"),
    mask: Optional[str] = Query(None, title="File Mask", description="Filter files by extension (e.g., '*.blend' or 'blend')"),
):
    """Возвращает дерево папок и файлов в заданном пути."""
    folder_path = Path(path)
    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    tree_data = get_folder_structure(folder_path, mask)
    return tree_data

@router.post("/create_folder")
def create_folder(request: CreateFolderRequest):
    """Создаёт папку и возвращает путь в нужном формате."""
    folder_path = Path(request.path)
    print(folder_path)

    try:
        folder_path.mkdir(parents=True, exist_ok=False)
        return {
            "message": f"Папка создана: {folder_path}",
            "full_path": os.path.normpath(str(folder_path)),
            "encoded_path": split_path_to_json(str(folder_path))
        }
    except FileExistsError:
        raise HTTPException(status_code=400, detail="Папка уже существует")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании папки: {str(e)}")
