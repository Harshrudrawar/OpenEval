class DomainError(Exception):
    """Base exception for domain errors."""


class ValidationError(DomainError):
    """Raised when a domain invariant is violated."""


class NotFoundError(DomainError):
    """Raised when a requested domain object cannot be found."""
