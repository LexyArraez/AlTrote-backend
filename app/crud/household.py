from sqlalchemy.orm import Session
from app.models.household import Household
from sqlalchemy import select

def get_household_by_invite_code(db: Session, invite_code: str) -> Household | None:
    stmt = select(Household).where(Household.invite_code == invite_code)
    return db.execute(stmt).scalar_one_or_none()

def create_household(db: Session, name: str, owner_id: int) -> Household:
    household = Household(name=name, owner_id=owner_id)
    db.add(household)
    db.flush()
    return household