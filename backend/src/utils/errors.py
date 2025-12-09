"""
Custom exception classes for the application.

All exceptions follow a standard JSON response format.
"""

from typing import Optional, Any, Dict


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to response dict."""
        return {
            "error": self.code,
            "message": self.message,
            "code": self.status_code,
            "details": self.details,
        }


class ValidationError(AppException):
    """Validation failed for request data."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class AuthenticationError(AppException):
    """Authentication failed (invalid credentials, missing token, etc.)."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationError(AppException):
    """User not authorized to access resource."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"

        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
        )


class ConflictError(AppException):
    """Resource already exists or state conflict."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class ServiceUnavailableError(AppException):
    """External service unavailable."""

    def __init__(self, service: str, message: Optional[str] = None):
        msg = f"{service} is temporarily unavailable"
        if message:
            msg += f": {message}"

        super().__init__(
            message=msg,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


class RateLimitError(AppException):
    """Rate limit exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message="Rate limit exceeded",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )
