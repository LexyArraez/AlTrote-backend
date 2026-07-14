from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister
from sqlalchemy import select

def get_user_by_firebase_id(db: Session, firebase_id: str) -> User | None:
    stmt = select(User).where(User.firebase_id == firebase_id)
    return db.execute(stmt).scalar_one_or_none()

def create_user(db: Session, firebase_id: str, email: str | None, data: UserRegister) -> User:
    user = User(
        firebase_id=firebase_id,
        email=email,
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.flush()
    return user