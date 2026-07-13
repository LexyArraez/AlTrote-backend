from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.firebase import verify_firebase_token
from app.database.db_connection import get_db
from app.models.enums import UserRole
from app.models.user import User

_bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:

    payload = verify_firebase_token(credentials.credentials)
    firebase_uid = payload["uid"]

    user = db.query(User).filter(User.firebase_id == firebase_uid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario autenticado en Firebase pero no registrado en la aplicacion",
        )
    return user


def require_role(role: UserRole):

    def _check_role(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Esta accion requiere rol '{role.value}'",
            )
        return current_user

    return _check_role