from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.firebase import verify_firebase_token
from app.database.db_connection import get_db
from app.models.enums import UserRole
from app.models.household import Household
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer_scheme = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: UserRegister,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    payload = verify_firebase_token(credentials.credentials)
    firebase_id = payload["uid"]
    email = payload.get("email")

    existing = db.query(User).filter(User.firebase_id == firebase_id).first()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Este usuario ya esta registrado")

    user = User(
        firebase_id=firebase_id,
        email=email,
        full_name=data.full_name,
        role=data.role,
    )

    if data.role == UserRole.HIJO:
        if not data.invite_code:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Falta el codigo de invitacion")
        household = db.query(Household).filter(Household.invite_code == data.invite_code).first()
        if not household:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Codigo de invitacion invalido")
        user.household_id = household.id

    db.add(user)
    db.commit()
    db.refresh(user)

    if data.role == UserRole.PADRE:
        household = Household(name=data.household_name or f"Familia de {user.full_name}", owner_id=user.id)
        db.add(household)
        db.commit()

    return user