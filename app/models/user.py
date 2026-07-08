from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.db_connection import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.household import Household

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))

    household_id: Mapped[int | None] = mapped_column(
        ForeignKey("household.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

        # Si es hijo: el nucleo familiar al que pertenece
    household: Mapped["Household | None"] = relationship(
        back_populates="children", foreign_keys=[household_id]
    )
        # Si es padre: el nucleo familiar que el mismo creo y posee
    owned_household: Mapped["Household | None"] = relationship(
        back_populates="owner", foreign_keys="Household.owner_id", uselist=False
    )
