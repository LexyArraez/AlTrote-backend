from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.enums import UserRole
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.task_validators import (obtener_household_del_padre,validar_hijo_pertenece_al_padre,verificar_pertenencia_tarea)

def create_task(db: Session, data: TaskCreate, padre: User) -> Task:
    household_id = obtener_household_del_padre(padre)
    validar_hijo_pertenece_al_padre(household_id, data.assigned_to_id, db)

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        frequency=data.frequency,
        points_value=data.points_value,
        assigned_to_id=data.assigned_to_id,
        created_by_id=padre.id,
        household_id=household_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db: Session, task_id: int) -> Task | None:
    query = select(Task).where(Task.id == task_id)
    return db.scalars(query).first()


def get_tasks_for_user(db: Session, current_user: User) -> list[Task]:
    if current_user.role == UserRole.PADRE:
        household = current_user.owned_household
        if not household:
            return []
        query = select(Task).where(Task.household_id == household.id)
        return list(db.scalars(query).all())

    query = select(Task).where(Task.assigned_to_id == current_user.id)
    return list(db.scalars(query).all())




def update_task(db: Session, task: Task, data: TaskUpdate, padre: User) -> Task:
    """Actualiza una tarea existente si pertenece al hogar del padre."""
    # 1. Validaciones de negocio externas
    household_id = obtener_household_del_padre(padre)
    verificar_pertenencia_tarea(task, household_id)

    if data.assigned_to_id is not None:
        validar_hijo_pertenece_al_padre(household_id, data.assigned_to_id, db)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task, padre: User) -> None:

    household_id = obtener_household_del_padre(padre)
    verificar_pertenencia_tarea(task, household_id)

    db.delete(task)
    db.commit()