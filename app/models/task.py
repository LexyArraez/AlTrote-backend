from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.db_connection import Base
from app.models.enums import TaskFrequency, TaskPriority, TaskStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.household import Household


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority"),
        nullable=False
    )
    frequency: Mapped[TaskFrequency] = mapped_column(
        Enum(TaskFrequency, name="task_frequency"),
        default=TaskFrequency.UNICA.value,
        server_default=TaskFrequency.UNICA.value
    )
    points_value: Mapped[int] = mapped_column(
        default=10,
        server_default="10"
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        default=TaskStatus.PENDIENTE,
        server_default=TaskStatus.PENDIENTE.value
    )


    household_id: Mapped[int] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"))
    assigned_to_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


    household: Mapped["Household"] = relationship(back_populates="tasks")

    assigned_to: Mapped["User"] = relationship(
        foreign_keys=[assigned_to_id],
        back_populates="assigned_tasks"
    )
    created_by: Mapped["User"] = relationship(
        foreign_keys=[created_by_id],
        back_populates="created_tasks"
    )
