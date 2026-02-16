class ServiceError(Exception):
    """Base error for service layer."""

class UserInputError(ServiceError):
    """User provided invalid input (show friendly message)."""

class NotFoundError(ServiceError):
    """There is not found entity (show friendly message)."""

class ConflictError(ServiceError):
    """Request conflicts with current state (e.g., duplicate)."""

class TemporaryError(ServiceError):
    """Temporary failure (db, network)."""