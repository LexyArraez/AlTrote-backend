from pydantic import BaseModel

from app.models.enums import UserRole


class UserRegister(BaseModel):
    full_name: str
    role: UserRole
    invite_code: str | None = None
    household_name: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    household_id: int | None
    level: int
    points_balance: int

    class Config:
        from_attributes = True