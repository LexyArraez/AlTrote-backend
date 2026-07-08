import enum


class UserRole(str, enum.Enum):

    PADRE = "padre"
    HIJO = "hijo"

class TaskPriority(int, enum.Enum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3
