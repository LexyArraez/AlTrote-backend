from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user, require_role
from app.database.db_connection import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get("/household/children", response_model=list[UserResponse])
def list_my_children(
    current_user: Annotated[User, Depends(require_role(UserRole.PADRE))],
    db: Annotated[Session, Depends(get_db)],
) -> list[User]:
    household = current_user.owned_household
    if household is None:
        return []
    return household.children