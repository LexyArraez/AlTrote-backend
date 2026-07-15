import secrets
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.db_connection import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


def generate_invite_code() -> str:
    return secrets.token_hex(4).upper()

class Household(Base):
    __tablename__ = 'household'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    invite_code: Mapped[str] = mapped_column(
        String(20), unique=True, default=generate_invite_code, index=True
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", use_alter=True, name="fk_household_owner_id"),
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())



    owner: Mapped["User"] = relationship(
        back_populates="owned_household", foreign_keys=[owner_id]
    )
    children: Mapped[list["User"]] = relationship(
        back_populates="household", foreign_keys="User.household_id"
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="household",
        cascade="all, delete-orphan"
    )