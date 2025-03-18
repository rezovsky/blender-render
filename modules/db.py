from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # ✅ Должно быть обязательно!

# ✅ Функция для получения сессии БД (используется в Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models.settings import Settings
    from models.blend_file import BlendFile
    from models.task import Task  # ✅ Добавляем Task
    Base.metadata.create_all(bind=engine)
