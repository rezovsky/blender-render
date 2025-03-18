from sqlalchemy import Column, Integer, String
from modules.db import Base

class BlendFile(Base):
    """
    Модель для хранения информации о .blend-файлах и результатах работы Blender-скрипта.
    """
    __tablename__ = "blend_files"

    id = Column(Integer, primary_key=True, index=True)
    
    # Полный путь к файлу (например: 'Z:/Projects/my_scene.blend')
    file_path = Column(String, unique=True, nullable=False)
    
    # Хэш от полного пути (например, md5("Z:/Projects/my_scene.blend"))
    path_hash = Column(String, nullable=False, index=True)
    
    # Хэш содержимого файла, если вы его вычисляете (например, md5 всех байт файла),
    # чтобы отслеживать изменения в самом .blend
    file_hash = Column(String, nullable=True, index=True)
    
    # Данные из скрипта Blender
    resolution_x = Column(Integer, nullable=True)
    resolution_y = Column(Integer, nullable=True)
    samples = Column(Integer, nullable=True)
    tile_size = Column(Integer, nullable=True)
    engine = Column(String, nullable=True)
    frame_current = Column(Integer, nullable=True)
    frame_start = Column(Integer, nullable=True)
    frame_end = Column(Integer, nullable=True)
    
    # Путь, заданный в сцене (scene.render.filepath)
    render_filepath = Column(String, nullable=True)
    
    # Путь к "превью" (сгенерированный Workbench/OpenGL рендер)
    preview_path = Column(String, nullable=True)

    def __repr__(self):
        return f"<BlendFile(file_path='{self.file_path}', engine='{self.engine}')>"
