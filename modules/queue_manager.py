import time
import threading
from sqlalchemy.exc import SQLAlchemyError
from modules.db import SessionLocal
from models.task import Task, TaskStatus
from models.settings import Settings
from modules.blender import run_render
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resume_crashed_tasks():
    """
    При запуске сервиса находит все задачи со статусом RUNNING
    и продолжает их рендер с сохранённого кадра.
    """
    db = SessionLocal()
    try:
        running_tasks = db.query(Task).filter(Task.status == TaskStatus.RUNNING).order_by(Task.position).all()
        for task in running_tasks:
            logger.info(
                f"Обнаружена незавершённая задача ID {task.id} (RUNNING). "
                f"Продолжаем с кадра {task.current_frame or task.frame_start}."
            )
            threading.Thread(target=run_render, args=(task.id,), daemon=True).start()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при возобновлении задач: {e}")
    finally:
        db.close()


def process_queue():
    """
    Фоновый процесс управления очередью рендера:
    1. При старте — восстанавливает все незавершённые (RUNNING) задачи.
    2. Если включён автостарт — берёт задачу из QUEUED и запускает её.
    """
    # ⚡ При запуске продолжаем незавершённые задачи
    resume_crashed_tasks()

    while True:
        db = SessionLocal()
        try:
            settings = db.query(Settings).first()
            if not settings or not settings.auto_start_queue:
                db.close()
                time.sleep(5)
                continue

            # Проверяем, не выполняется ли уже задача
            running_task = db.query(Task).filter(Task.status == TaskStatus.RUNNING).first()
            if running_task:
                db.close()
                time.sleep(5)
                continue

            # Берём первую задачу в очереди (только QUEUED)
            task = (
                db.query(Task)
                .filter(Task.status == TaskStatus.QUEUED)
                .order_by(Task.position)
                .first()
            )

            if task:
                logger.info(f"Запуск задачи ID {task.id} из очереди.")
                db.close()

                # ⚡ Запускаем рендер в отдельном потоке
                threading.Thread(target=run_render, args=(task.id,), daemon=True).start()

            else:
                db.close()
                time.sleep(5)

        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных: {e}")
            db.rollback()
            db.close()
            time.sleep(5)

        except Exception as e:
            logger.error(f"Ошибка в процессе очереди: {e}")
            db.close()
            time.sleep(5)
