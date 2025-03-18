from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routes.settings import router as settings_router
from routes.files import router as files_router
from routes.folder import router as folder_router
from routes.browser import router as browser_router
from routes.tasks import router as tasks_router
from modules.db import init_db
from modules.queue_manager import process_queue  # Импорт менеджера очереди

import os
import logging
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Включаем отладочные логи
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Разрешённые CORS-оригины
origins = [
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
init_db()

# Подключение маршрутов
app.include_router(settings_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(folder_router, prefix="/api")
app.include_router(browser_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# Подключение статических файлов (CSS, JS)
css_directory = os.path.join(os.getcwd(), "web", "dist", "css")
app.mount("/css", StaticFiles(directory=css_directory), name="css")

js_directory = os.path.join(os.getcwd(), "web", "dist", "js")
app.mount("/js", StaticFiles(directory=js_directory), name="js")

static_directory = os.path.join(os.getcwd(), "web", "dist")

# Папка с превью рендеров
previews_dir = os.path.join(os.getcwd(), "previews")

# Проверяем, существует ли папка, если нет — создаём
if not os.path.exists(previews_dir):
    os.makedirs(previews_dir)

app.mount("/previews", StaticFiles(directory=previews_dir), name="previews")

# Запуск менеджера очереди при старте приложения
def startup_event():
    """Запускает фоновый процесс управления очередью при старте FastAPI."""
    logger.info("Запуск фонового процесса управления очередью")
    thread = threading.Thread(target=process_queue, daemon=True)
    thread.start()

@app.on_event("startup")
async def startup():
    startup_event()

# Главная страница (рендерит index.html)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_file_path = os.path.join(static_directory, "index.html")
    if os.path.exists(html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content=content)
    return HTMLResponse(content="Index file not found.", status_code=404)
