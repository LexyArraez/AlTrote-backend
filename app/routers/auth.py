from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_firebase_payload
from app.database.db_connection import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse
from app.core import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: UserRegister,
    payload: Annotated[dict, Depends(get_firebase_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    return auth_service.register_user(db, payload, data)