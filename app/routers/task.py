from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.db_connection import get_db
from app.auth.dependencies import get_current_user, require_role
from app.crud import task as task_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse,TaskCompleteResponse
from app.exceptions import TaskNotFound, TaskNotVisible, WrongRole


from app.crud.task import (get_task,get_tasks_for_user,create_task,update_task,delete_task)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/",response_model=TaskResponse,status_code=status.HTTP_201_CREATED,summary="Crear una nueva tarea (Solo Padres)")
def api_create_task(
        data: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.PADRE:
        raise WrongRole(required_role=UserRole.PADRE.value)

    return create_task(db=db, data=data, padre=current_user)


@router.get("/",response_model=list[TaskResponse],summary="Listar tareas asociadas al usuario")
def api_get_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return get_tasks_for_user(db=db, current_user=current_user)


@router.get("/{task_id}",response_model=TaskResponse,summary="Obtener detalles de una tarea específica")
def api_get_task_by_id(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    task = get_task(db=db, task_id=task_id)
    if not task:
        raise TaskNotFound()

    if current_user.role == UserRole.PADRE:
        household = current_user.owned_household
        if not household or task.household_id != household.id:
            raise TaskNotVisible()
    else:
        if task.assigned_to_id != current_user.id:
            raise TaskNotVisible()

    return task

@router.post("/{task_id}/complete", response_model=TaskCompleteResponse, summary="Marcar una tarea como completada (Solo Hijos)")
def api_complete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.HIJO:
        raise WrongRole(required_role=UserRole.HIJO.value)

    task = get_task(db=db, task_id=task_id)
    if not task:
        raise TaskNotFound()

    updated_task, level_up = task_crud.complete_task(db=db, task=task, current_user=current_user)

    return {
        "task": updated_task,
        "points_balance": current_user.points_balance,
        "level": current_user.level,
        "level_up": level_up,
    }

@router.put("/{task_id}",response_model=TaskResponse,summary="Actualizar una tarea (Solo Padres)")
def api_update_task(
        task_id: int,
        data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.PADRE:
        raise WrongRole(required_role=UserRole.PADRE.value)

    task = get_task(db=db, task_id=task_id)
    if not task:
        raise TaskNotFound()

    return update_task(db=db, task=task, data=data, padre=current_user)


@router.delete("/{task_id}",status_code=status.HTTP_204_NO_CONTENT,summary="Eliminar una tarea (Solo Padres)")
def api_delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.PADRE:
        raise WrongRole(required_role=UserRole.PADRE.value)

    task = get_task(db=db, task_id=task_id)
    if not task:
        raise TaskNotFound()

    delete_task(db=db, task=task, padre=current_user)
    return None