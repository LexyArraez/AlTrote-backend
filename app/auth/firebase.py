import firebase_admin
from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.config import settings

_cred = credentials.Certificate(settings.firebase_credentials_path)
firebase_admin.initialize_app(_cred)


def verify_firebase_token(id_token: str) -> dict:

    try:
        return firebase_auth.verify_id_token(id_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacion invalido o expirado",
        ) from exc