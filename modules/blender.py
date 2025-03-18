import subprocess
import re
import os
from sqlalchemy.orm import Session
from models.task import Task, TaskStatus
from modules.db import SessionLocal

def parse_blender_output(line, task, db):
    """ Парсит вывод Blender и обновляет прогресс в БД """
    frame_match = re.search(r"Fra:(\d+)", line)
    if frame_match:
        task.current_frame = int(frame_match.group(1))

    tile_match = re.search(r"Rendered (\d+)/(\d+) Tiles, Sample (\d+)/(\d+)", line)
    if tile_match:
        current_tile = int(tile_match.group(1))
        total_tiles = max(int(tile_match.group(2)), 1)
        current_sample = int(tile_match.group(3))
        total_samples = max(int(tile_match.group(4)), 1)

        task.current_tile = current_tile
        task.current_sample = current_sample

        if task.frame_end and task.frame_start and task.frame_end != task.frame_start:
            total_frames = max(task.frame_end - task.frame_start + 1, 1)
            frame_progress = 100 / total_frames
            tile_progress = frame_progress / total_tiles
            sample_progress = tile_progress / total_samples

            completed_frames = (task.current_frame or task.frame_start) - task.frame_start
            task.progress = round(
                completed_frames * frame_progress +
                current_tile * tile_progress +
                current_sample * sample_progress, 2
            )
        else:
            tile_progress = 100 / total_tiles
            sample_progress = tile_progress / total_samples
            task.progress = round(
                current_tile * tile_progress + current_sample * sample_progress, 2
            )

        db.commit()

def pause_running_tasks(db: Session):
    """Ставит на паузу текущие задачи и убивает процессы."""
    running_tasks = db.query(Task).filter(Task.status == TaskStatus.RUNNING).all()
    for running_task in running_tasks:
        if running_task.pid:
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(running_task.pid)], check=True)
            except subprocess.CalledProcessError:
                pass  # процесс уже завершён
            running_task.status = TaskStatus.PAUSED
            running_task.pid = None
            db.commit()

def run_render(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        return

    # Проверяем и ставим на паузу другие запущенные задачи
    pause_running_tasks(db)

    # Продолжаем с места паузы или начинаем заново
    if task.status == TaskStatus.PAUSED and task.current_frame:
        start_frame = task.current_frame
    else:
        start_frame = task.frame_start or task.frame or 1
        task.progress = 0.0
        task.current_frame = start_frame
        task.current_tile = 0
        task.current_sample = 0

    task.status = TaskStatus.RUNNING
    db.commit()

    command = [
        "blender",
        "-b",
        task.file_path,
        "-o", os.path.join(task.selected_folder, "frame_#####"),
        "-s", str(start_frame),
        "-e", str(task.frame_end or start_frame),
        "-a"
    ]

    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        task.pid = proc.pid
        db.commit()

        for line in proc.stdout:
            parse_blender_output(line, task, db)
            db.refresh(task)

            if task.status in (TaskStatus.PAUSED, TaskStatus.STOPPED):
                proc.kill()
                break

        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.current_frame = None
            task.current_tile = None
            task.current_sample = None
        elif task.status == TaskStatus.STOPPED:
            task.current_frame = None
            task.current_tile = None
            task.current_sample = None
            task.progress = 0

        task.pid = None
        db.commit()
        db.close()

def pause_render(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task and task.pid:
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(task.pid)], check=True)
        except subprocess.CalledProcessError:
            pass
        finally:
            task.pid = None  # PID процесса сбрасываем, так как процесс убит
            task.status = TaskStatus.PAUSED  # Задача переходит в PAUSED
            db.commit()
    db.close()

def stop_render(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task and task.pid:
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(task.pid)], check=True)
        except subprocess.CalledProcessError:
            pass
        finally:
            task.pid = None
            task.status = TaskStatus.STOPPED
            task.progress = 0
            task.current_frame = None
            task.current_tile = None
            task.current_sample = None
            db.commit()
    db.close()

