import enum


class UserRole(str, enum.Enum):

    PADRE = "padre"
    HIJO = "hijo"
