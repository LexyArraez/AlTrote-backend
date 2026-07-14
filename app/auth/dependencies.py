from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, joinedload  # <- Añadido joinedload para rendimiento

from app.auth.firebase import verify_firebase_token
from app.database.db_connection import get_db
from app.models.enums import UserRole
from app.models.user import User

_bearer_scheme = HTTPBearer()


def get_firebase_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> dict:
    """
    Extrae el token de los headers de autorización y lo valida contra Firebase.
    """
    try:
        return verify_firebase_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc


def get_current_user(
    payload: Annotated[dict, Depends(get_firebase_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Busca al usuario autenticado de Firebase en la base de datos de la app.
    Trae las relaciones de hogar de inmediato para optimizar consultas posteriores.
    """
    firebase_uid = payload["uid"]

    user = (
        db.query(User)
        .options(
            joinedload(User.owned_household),
            joinedload(User.household)
        )
        .filter(User.firebase_id == firebase_uid)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario autenticado en Firebase pero no registrado en la aplicación",
        )
    return user


def require_role(*roles: UserRole):
    """
    Fábrica de dependencias para restringir endpoints según el rol del usuario.
    Permite validar uno o múltiples roles permitidos.
    """
    def _check_role(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            allowed = ", ".join(r.value for r in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Esta acción requiere uno de los siguientes roles: {allowed}",
            )
        return current_user

    return _check_role