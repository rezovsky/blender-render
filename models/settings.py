from sqlalchemy import Column, String, Boolean
from modules.db import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(String, primary_key=True, default="main")
    blender_mode = Column(String, nullable=False, default="path")  # "path" или "manual"
    blender_path = Column(String, nullable=True)  # Указывается вручную, если `blender_mode="manual"`
    projects_path = Column(String, nullable=True)
    use_render_folder = Column(Boolean, default=False)  # Использовать отдельную папку рендера?
    render_folder_path = Column(String, nullable=True)  # Путь к рендер-папке
    auto_start_queue = Column(Boolean, default=False)  # Запуск очереди при старте сервера?
    auto_start_tasks = Column(Boolean, default=False)  # Запуск задачи сразу после добавления?
