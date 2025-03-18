import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from modules.db import SessionLocal
from models.settings import Settings
from pydantic import BaseModel
from utils.path_utils import split_path_to_json, join_path_from_json


router = APIRouter()

class SettingsSchema(BaseModel):
    blender_mode: str = "path"
    blender_path: str | None = None
    projects_path: str | None = None
    use_render_folder: bool = False
    render_folder_path: str | None = None
    auto_start_queue: bool = False
    auto_start_tasks: bool = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.put("/settings/")
def update_settings(new_settings: SettingsSchema, db: Session = Depends(get_db)):
    print("Полученные настройки:", new_settings.dict())

    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    # 🔥 Сохраняем пути как JSON
    settings.blender_mode = new_settings.blender_mode
    settings.blender_path = new_settings.blender_path
    settings.projects_path = split_path_to_json(new_settings.projects_path)
    settings.use_render_folder = new_settings.use_render_folder
    settings.render_folder_path = split_path_to_json(new_settings.render_folder_path)
    settings.auto_start_queue = new_settings.auto_start_queue
    settings.auto_start_tasks = new_settings.auto_start_tasks

    print("Сохранение настроек в БД:", settings.__dict__)

    db.commit()
    db.refresh(settings)

    print("Настройки после коммита:", settings.__dict__)

    return {"message": "Настройки обновлены"}

@router.get("/settings/", response_model=SettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()

    return SettingsSchema(
        blender_mode=settings.blender_mode,
        blender_path=settings.blender_path,
        projects_path=join_path_from_json(settings.projects_path),
        use_render_folder=settings.use_render_folder,
        render_folder_path=join_path_from_json(settings.render_folder_path),
        auto_start_queue=settings.auto_start_queue,
        auto_start_tasks=settings.auto_start_tasks
    )
