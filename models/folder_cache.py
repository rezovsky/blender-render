# models/folder_cache.py
from sqlalchemy import Column, String, JSON
from modules.db import Base

class FolderCache(Base):
    __tablename__ = "folder_cache"

    path_hash = Column(String, primary_key=True)  # Уникальный ID, теперь учитывает и путь, и маску
    path = Column(JSON, nullable=False)           # Путь в виде массива
    mask = Column(String, nullable=True)          # Сама маска (например, "*.blend")
    data = Column(JSON, nullable=False)           # Структура папок/файлов
