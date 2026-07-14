from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


class HouseholdResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    children: list[UserResponse]

    model_config = ConfigDict(from_attributes=True)