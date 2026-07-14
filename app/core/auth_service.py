from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import household as household_crud
from app.crud import user as user_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserRegister

def register_user(db: Session, payload: dict, data: UserRegister) -> User:
    firebase_id = payload["uid"]
    email = payload.get("email")

    if user_crud.get_user_by_firebase_id(db, firebase_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Este usuario ya esta registrado")

    household_id = None
    if data.role == UserRole.HIJO:
        household_id = _resolve_child_household(db, data.invite_code)

    user = user_crud.create_user(db, firebase_id, email, data)
    if household_id:
        user.household_id = household_id

    if data.role == UserRole.PADRE:
        household_name = data.household_name or f"Familia de {user.full_name}"
        household_crud.create_household(db, household_name, user.id)

    db.commit()
    db.refresh(user)
    return user

def _resolve_child_household(db: Session, invite_code: str | None) -> int:
    if not invite_code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Falta el codigo de invitacion")
    household = household_crud.get_household_by_invite_code(db, invite_code)
    if not household:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Codigo de invitacion invalido")
    return household.id