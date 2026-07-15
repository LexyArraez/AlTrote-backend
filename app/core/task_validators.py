from sqlalchemy.orm import Session
from app.models.enums import UserRole
from app.models.task import Task
from app.models.user import User
from app.exceptions import (HouseholdNotFound,ChildNotInHousehold,TaskNotBelongingToHousehold,)


def obtener_household_del_padre(padre: User) -> int:
    """Valido que el padre tenga un hogar y retorna su ID."""
    household = padre.owned_household
    if not household:
        raise HouseholdNotFound()
    return household.id


def validar_hijo_pertenece_al_padre(padre_household_id: int, hijo_id: int, db: Session) -> None:

    hijo_existe = db.query(User).filter(
        User.id == hijo_id,
        User.household_id == padre_household_id,
        User.role == UserRole.HIJO
    ).first()

    if not hijo_existe:
        raise ChildNotInHousehold()


def verificar_pertenencia_tarea(task: Task, household_id: int) -> None:

    if task.household_id != household_id:
        raise TaskNotBelongingToHousehold()