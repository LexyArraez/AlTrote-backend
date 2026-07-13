import firebase_admin
from fastapi import HTTPException
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.config import settings

_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def verify_firebase_token(id_token: str) -> dict:
    try:
        _get_firebase_app()
        return firebase_auth.verify_id_token(id_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token invalido o expirado") from exc