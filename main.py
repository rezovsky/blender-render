from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from routes.settings import router as settings_router
from routes.files import router as files_router
from routes.folder import router as folder_router
from routes.browser import router as browser_router
from routes.tasks import router as tasks_router
from modules.db import init_db
from modules.queue_manager import process_queue

import os
import logging
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000"  # если фронт в dev режиме на Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД
init_db()

# Подключаем API-маршруты
app.include_router(settings_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(folder_router, prefix="/api")
app.include_router(browser_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# Подключаем статику из сборки Vite
static_directory = os.path.join(os.getcwd(), "web", "dist")
app.mount("/", StaticFiles(directory=static_directory, html=True), name="static")

# Папка для превью рендеров
previews_dir = os.path.join(os.getcwd(), "previews")
if not os.path.exists(previews_dir):
    os.makedirs(previews_dir)
app.mount("/previews", StaticFiles(directory=previews_dir), name="previews")

# Фоновый запуск очереди
def startup_event():
    logger.info("Запуск фонового процесса управления очередью")
    thread = threading.Thread(target=process_queue, daemon=True)
    thread.start()

@app.on_event("startup")
async def startup():
    startup_event()
