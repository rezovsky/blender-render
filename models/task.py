from sqlalchemy import Column, Integer, String, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from pydantic import BaseModel
from modules.db import Base
import enum

class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    DELETED = "deleted"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    render_type: Mapped[str] = mapped_column(String, nullable=False)
    frame: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    frame_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    frame_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    selected_folder: Mapped[str] = mapped_column(String, nullable=False)
    resolution_x: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_y: Mapped[int] = mapped_column(Integer, nullable=False)
    samples: Mapped[int] = mapped_column(Integer, nullable=False)
    tile_size: Mapped[int] = mapped_column(Integer, nullable=False)
    engine: Mapped[str] = mapped_column(String, nullable=False)
    preview_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.QUEUED, nullable=False)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_frame: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_tile: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_sample: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pid = Column(Integer, nullable=True)


class TaskBase(BaseModel):
    file_path: str
    render_type: str
    frame: Optional[int] = None
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    selected_folder: str
    resolution_x: int
    resolution_y: int
    samples: int
    tile_size: int
    engine: str
    preview_path: Optional[str] = None
    status: TaskStatus
    progress: float
    current_frame: Optional[int] = None
    current_tile: Optional[int] = None
    current_sample: Optional[int] = None
    pid: Optional[int] = None


class TaskCreate(BaseModel):
    file_path: str
    render_type: str
    frame: Optional[int] = None
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    selected_folder: str
    resolution_x: int
    resolution_y: int
    samples: int
    tile_size: int
    engine: str
    preview_path: Optional[str] = None
    status: TaskStatus = TaskStatus.QUEUED
    progress: float = 0.0
    current_frame: Optional[int] = None
    current_tile: Optional[int] = None
    current_sample: Optional[int] = None 
    pid: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
