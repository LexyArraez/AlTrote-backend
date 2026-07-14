import enum


class UserRole(str, enum.Enum):

    PADRE = "padre"
    HIJO = "hijo"

class TaskPriority(int, enum.Enum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3

class TaskStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class TaskFrequency(str, enum.Enum):
    UNICA = "unica"
    DIARIA = "diaria"
    SEMANAL = "semanal"


