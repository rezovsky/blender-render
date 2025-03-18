from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc
from models.task import Task, TaskCreate, TaskResponse, TaskStatus
from modules.db import get_db
from modules.blender import run_render, stop_render, pause_render
from typing import List
from sqlalchemy.sql import func
from fastapi import BackgroundTasks

router = APIRouter()

@router.post("/tasks/add", response_model=TaskResponse)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    max_position = db.query(func.max(Task.position)).scalar() or 0

    new_task = Task(
        file_path=task.file_path,
        render_type=task.render_type,
        frame=task.frame,
        frame_start=task.frame_start,
        frame_end=task.frame_end,
        selected_folder=task.selected_folder,
        resolution_x=task.resolution_x,
        resolution_y=task.resolution_y,
        samples=task.samples,
        tile_size=task.tile_size,
        engine=task.engine,
        preview_path=task.preview_path,
        status=TaskStatus.QUEUED,
        progress=0.0,
        current_frame=None,
        current_tile = None,
        position=max_position + 1
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/tasks/queue/", response_model=List[TaskResponse])
def get_task_queue(db: Session = Depends(get_db)):
    tasks = (
        db.query(Task)
        .filter(Task.status != TaskStatus.DELETED)
        .order_by(asc(Task.position))
        .all()
    )

    return tasks


@router.delete("/tasks/delete/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.status = TaskStatus.DELETED
    db.commit()
    return {"message": f"Задача {task_id} помечена как удалённая"}


@router.put("/tasks/reorder")
def reorder_tasks(tasks: List[dict], db: Session = Depends(get_db)):
    """Принимает список задач с новым порядком"""
    for item in tasks:
        task = db.query(Task).filter(Task.id == item["id"]).first()
        if task and task.status != TaskStatus.DELETED:
            task.position = item["position"]

    db.commit()
    return {"message": "Очередь переупорядочена успешно"}


@router.post("/tasks/start/{task_id}")
def start_task(task_id: int, background_tasks: BackgroundTasks):
    """Запускает рендер задачи, ничего не обновляет в БД, только вызывает run_render()."""
    
    background_tasks.add_task(run_render, task_id)

    return {"message": f"Задача {task_id} запущена"}


@router.post("/tasks/pause/{task_id}")
def pause_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.status != TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Задача не выполняется")

    pause_render(task_id)  # ✅ Завершаем процесс без сброса прогресса

    # Перечитываем задачу после паузы
    db.refresh(task)

    return {
        "message": f"Задача {task_id} приостановлена",
        "status": task.status.value
    }



@router.post("/tasks/stop/{task_id}")
def stop_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Полный сброс задачи, рендер начинается с нуля при следующем запуске
    task.status = TaskStatus.STOPPED
    task.current_frame = None
    task.current_tile = None
    task.progress = 0.0
    db.commit()
    stop_render(task_id)  # Убиваем процесс

    return {
        "message": f"Задача {task_id} остановлена",
        "status": task.status.value
    }
