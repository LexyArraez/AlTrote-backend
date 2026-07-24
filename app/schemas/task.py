from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskFrequency, TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str | None = Field(None, max_length=1000)
    priority: TaskPriority
    frequency: TaskFrequency = TaskFrequency.UNICA
    points_value: int = Field(10, ge=0)


class TaskCreate(TaskBase):
    """Nota: created_by_id y household_id se obtendrán directamente del usuario
    autenticado (el Padre) en el endpoint para evitar manipulaciones.
    """
    assigned_to_id: int


class TaskUpdate(TaskBase):
    title: str | None = Field(None, min_length=3, max_length=150)
    description: str | None = Field(None, max_length=1000)
    priority: TaskPriority | None = None
    frequency: TaskFrequency | None = None
    points_value: int | None = Field(None, ge=0)
    assigned_to_id: int | None = None
    status: TaskStatus | None = None


class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    household_id: int
    assigned_to_id: int
    created_by_id: int
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class TaskCompleteResponse(BaseModel):

    task: TaskResponse
    points_balance: int
    level: int
    level_up: bool

    class Config:
        from_attributes = True