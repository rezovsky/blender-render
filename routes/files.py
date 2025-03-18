import logging
import subprocess
import json
import os
import hashlib
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from modules.db import SessionLocal
from models.settings import Settings
from models.blend_file import BlendFile  # Импортируем модель
from utils.path_utils import split_path_to_json, join_path_from_json  # Импортируем обработку путей

router = APIRouter()
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_relative_preview_path(full_preview_path: str) -> str:
    if not full_preview_path:
        return ""
    base_path = os.getcwd()
    return full_preview_path.replace(base_path, "").replace("\\", "/")

def get_blender_path(db: Session):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=500, detail="Настройки не найдены")
    
    if settings.blender_mode == "manual" and settings.blender_path:
        return join_path_from_json(settings.blender_path)
    return "blender"

def calculate_file_hash(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

@router.get("/file_info")
def get_blend_file_info(
    file_path: str = Query(..., description="Путь к .blend файлу"),
    db: Session = Depends(get_db)
):
    """Ищет информацию в БД, если данных нет или хэш изменился — обновляет и снова запрашивает из БД"""
    logger.info(f"Запрос на файл: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        raise HTTPException(status_code=400, detail="Файл не найден")

    path_hash = hashlib.md5(file_path.encode("utf-8")).hexdigest()
    file_hash = calculate_file_hash(file_path)

    # Проверяем данные в БД
    db_file = db.query(BlendFile).filter(BlendFile.path_hash == path_hash).first()

    if db_file and db_file.file_hash == file_hash:
        logger.info("Данные найдены в БД, и хэш не изменился. Возвращаем данные из базы.")
    else:
        logger.info("Данных нет или хэш изменился. Обновляем информацию.")
        blender_path = get_blender_path(db)

        script_template_path = "blender_script_template.py"
        if not os.path.exists(script_template_path):
            raise HTTPException(status_code=500, detail="Файл-шаблон для Blender не найден")

        with open(script_template_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        safe_file_path = file_path.replace("\\", "\\\\")
        script_content = script_content.replace("{file_path}", safe_file_path)

        temp_script_path = "temp_blender_script.py"
        with open(temp_script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        cmd = [blender_path, "--background", "--python", temp_script_path]
        logger.info(f"Команда для запуска Blender: {cmd}")

        process = subprocess.run(cmd, capture_output=True, text=True)

        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

        if process.returncode != 0:
            logger.error(f"Ошибка Blender: {process.stderr.strip()}")
            raise HTTPException(status_code=500, detail=f"Ошибка Blender: {process.stderr.strip()}")

        try:
            json_start = process.stdout.find("{")
            if json_start == -1:
                raise HTTPException(status_code=500, detail="Ошибка: JSON не найден в выводе Blender")

            clean_output = process.stdout[json_start:]
            response_data = json.loads(clean_output)

            if "error" in response_data:
                logger.error(f"Ошибка внутри Blender: {response_data['error']}")
                raise HTTPException(status_code=500, detail=f"Ошибка Blender: {response_data['error']}")

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}. Ответ Blender: {process.stdout.strip()}")
            raise HTTPException(status_code=500, detail="Ошибка обработки данных Blender: JSONDecodeError")

        if db_file:
            logger.info("Файл найден в БД, но хэш изменился. Обновляем данные.")
            db_file.file_hash = file_hash
            db_file.resolution_x = response_data.get("resolution_x")
            db_file.resolution_y = response_data.get("resolution_y")
            db_file.samples = response_data.get("samples")
            db_file.tile_size = response_data.get("tile_size")
            db_file.engine = response_data.get("engine")
            db_file.frame_current = response_data.get("frame_current")
            db_file.frame_start = response_data.get("frame_start")
            db_file.frame_end = response_data.get("frame_end")
            db_file.render_filepath = response_data.get("render_filepath")
            db_file.preview_path = get_relative_preview_path(response_data.get("preview_path"))
        else:
            logger.info("Файл не найден в БД. Создаём новую запись.")
            db_file = BlendFile(
                file_path=split_path_to_json(file_path),
                path_hash=path_hash,
                file_hash=file_hash,
                resolution_x=response_data.get("resolution_x"),
                resolution_y=response_data.get("resolution_y"),
                samples=response_data.get("samples"),
                tile_size=response_data.get("tile_size"),
                engine=response_data.get("engine"),
                frame_current=response_data.get("frame_current"),
                frame_start=response_data.get("frame_start"),
                frame_end=response_data.get("frame_end"),
                render_filepath=response_data.get("render_filepath"),
                preview_path=get_relative_preview_path(response_data.get("preview_path"))
            )
            db.add(db_file)

        db.commit()
        db.refresh(db_file)

        logger.info("Обновлённые данные успешно сохранены в БД.")

    # ✅ Финальный запрос в БД, чтобы убедиться, что возвращаем данные только оттуда
    db_file = db.query(BlendFile).filter(BlendFile.path_hash == path_hash).first()
    if not db_file:
        raise HTTPException(status_code=500, detail="Ошибка: данные не записались в БД")

    # ✅ Гарантируем, что возвращаем JSON-объект, а не строку
    db_file_dict = db_file.__dict__.copy()
    db_file_dict["file_path"] = join_path_from_json(db_file.file_path)

    return db_file_dict
