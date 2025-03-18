import os
import logging
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.settings import router as settings_router
from routes.files import router as files_router
from routes.folder import router as folder_router
from routes.browser import router as browser_router
from routes.tasks import router as tasks_router
from modules.db import init_db
from modules.queue_manager import process_queue

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Создаём FastAPI приложение
app = FastAPI()

# Настройка CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
init_db()

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Подключаем API-маршруты
app.include_router(settings_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(folder_router, prefix="/api")
app.include_router(browser_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# Подключаем папку для превью рендеров
previews_dir = os.path.join(BASE_DIR, "previews")
if not os.path.exists(previews_dir):
    os.makedirs(previews_dir)
app.mount("/previews", StaticFiles(directory=previews_dir), name="previews")

# Эндпоинт для отладки
@app.get("/debug_previews")
async def debug_previews():
    return {"mounted_previews_dir": previews_dir, "files": os.listdir(previews_dir)}

# Фоновый запуск очереди
def startup_event():
    logger.info("Запуск фонового процесса управления очередью")
    thread = threading.Thread(target=process_queue, daemon=True)
    thread.start()

@app.on_event("startup")
async def startup():
    startup_event()

# Подключаем статику из сборки Vite — в САМОМ КОНЦЕ!
static_directory = os.path.join(BASE_DIR, "web", "dist")
app.mount("/", StaticFiles(directory=static_directory, html=True), name="static")
