from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserResponse, HouseholdResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get("/household", response_model=HouseholdResponse)
def get_my_household(
    current_user: Annotated[User, Depends(require_role(UserRole.PADRE))],
):
    household = current_user.owned_household
    if household is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No tienes un nucleo familiar creado")
    return household


@router.get("/household/children", response_model=list[UserResponse])
def list_my_children(
    current_user: Annotated[User, Depends(require_role(UserRole.PADRE))]
) -> list[User]:
    household = current_user.owned_household
    if household is None:
        return []
    return household.children

