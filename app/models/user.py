from datetime import datetime
from typing import ClassVar, TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.db_connection import Base
from app.models.enums import TaskPriority, UserRole

if TYPE_CHECKING:
    from app.models.household import Household


class User(Base):
    __tablename__ = "users"

    TASKS_PER_LEVEL: ClassVar[int] = 5
    LEVEL_UP_BONUS_POINTS: ClassVar[int] = 100

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    household_id: Mapped[int | None] = mapped_column(
        ForeignKey("household.id"), nullable=True
    )

    household: Mapped["Household | None"] = relationship(
        back_populates="children",
        foreign_keys=[household_id]
    )

    owned_household: Mapped["Household | None"] = relationship(
        back_populates="owner",
        foreign_keys="Household.owner_id",
        uselist=False
    )

    completed_tasks: Mapped[int] = mapped_column(default=0, server_default="0")
    level: Mapped[int] = mapped_column(default=1, server_default="1")
    tasks_toward_level: Mapped[int] = mapped_column(default=0, server_default="0")
    points_balance: Mapped[int] = mapped_column(default=0, server_default="0")


    @property
    def is_child(self) -> bool:
        return self.role == UserRole.HIJO

    @property
    def tasks_to_next_level(self) -> int:
        return self.TASKS_PER_LEVEL - self.tasks_toward_level

    @property
    def required_priority_for_level_up(self) -> TaskPriority:
        """Determina la prioridad mínima requerida según el nivel actual."""
        if self.level == 1:
            return TaskPriority.BAJA
        if self.level == 2:
            return TaskPriority.MEDIA
        return TaskPriority.ALTA


    def register_completed_task(self, priority: TaskPriority, task_points: int) -> bool:
        """
        Registra una tarea completada por el usuario.
        Suma puntos y evalúa si sube de nivel (solo si cumple los requisitos de prioridad).
        """
        if not self.is_child:
            raise ValueError("Solo los usuarios con rol 'Hijo' pueden acumular puntos.")

        self.completed_tasks += 1
        self.points_balance += task_points

        if priority.value < self.required_priority_for_level_up.value:
            return False

        self.tasks_toward_level += 1

        if self.tasks_toward_level >= self.TASKS_PER_LEVEL:
            self._trigger_level_up()
            return True

        return False

    def _trigger_level_up(self) -> None:
        """Encapsula la lógica interna de subir de nivel."""
        self.level += 1
        self.tasks_toward_level = 0
        self.points_balance += self.LEVEL_UP_BONUS_POINTS
