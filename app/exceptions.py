from fastapi import status


class AppException(Exception):


    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Ha ocurrido un error"

    def __init__(self, detail: str | None = None) -> None:
        # Si se pasa un detalle personalizado al instanciarla, lo usamos.
        # Si no, mantenemos el valor estático definido en la clase.
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)

# --- Categorías base, por tipo de error HTTP ---


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Recurso no encontrado"


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "No tienes permiso para realizar esta acción"


class BadRequestError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Petición inválida"


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "El recurso ya existe"



# --- TAREAS ---

class TaskNotFound(NotFoundError):
    detail = "Tarea no encontrada"


class TaskNotBelongingToHousehold(ForbiddenError):
    """Reemplaza a TaskNotOwnedByParent para soportar permisos a nivel de hogar."""
    detail = "Esta tarea no pertenece al núcleo familiar de tu cuenta"


class TaskNotVisible(ForbiddenError):
    detail = "No puedes ver esta tarea"


class TaskAlreadyCompleted(ConflictError):
    """Evita que un hijo reclame los puntos de una tarea que ya finalizó."""
    detail = "Esta tarea ya ha sido marcada como completada"


class TaskNotPendingApproval(BadRequestError):
    """Evita que el padre intente aprobar tareas activas o ya cobradas."""
    detail = "La tarea no está en espera de aprobación por un adulto"


# --- HOGAR / FAMILIA ---

class HouseholdNotFound(NotFoundError):
    detail = "No tienes un núcleo familiar creado"


class MissingInviteCode(BadRequestError):
    detail = "Falta el código de invitación"


class InvalidInviteCode(BadRequestError):
    detail = "Código de invitación inválido"


# --- USUARIOS Y ROLES ---

class UserNotRegistered(NotFoundError):
    detail = "Usuario autenticado en Firebase pero no registrado en la aplicación"


class UserAlreadyRegistered(ConflictError):
    detail = "Este usuario ya está registrado"


class UserAlreadyHasHousehold(ConflictError):
    """Evita que un usuario intente unirse a otra familia si ya tiene una activa."""
    detail = "Ya perteneces a un núcleo familiar"


class ChildNotInHousehold(BadRequestError):
    detail = "El usuario asignado no es un hijo vinculado a tu núcleo familiar"


class WrongRole(ForbiddenError):
    def __init__(self, required_role: str, detail: str | None = None) -> None:
        message = detail or f"Esta acción requiere el rol de '{required_role}'"
        super().__init__(message)
