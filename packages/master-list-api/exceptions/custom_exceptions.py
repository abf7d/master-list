# app/exceptions/custom_exceptions.py
from typing import Any, Dict, List, Optional


class APIError(Exception):
    """Base exception for API errors"""
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

class NotFoundError(APIError):
    def __init__(
        self, 
        message: str = "Resource not found", 
        error_code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code=error_code,
            details=details
        )

class DatabaseError(APIError):
    def __init__(
        self, 
        message: str = "Database error occurred", 
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code=error_code,
            details=details
        )

class AuthenticationError(APIError):
    def __init__(
        self, 
        message: str = "Authentication failed", 
        error_code: str = "AUTHENTICATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
            details=details
        )

class ForbiddenError(APIError):
    def __init__(
        self, 
        message: str = "Access forbidden", 
        error_code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
            details=details
        )

class ValidationError(APIError):
    def __init__(
        self, 
        message: str = "Validation error", 
        error_code: str = "VALIDATION_ERROR",
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        details = {"errors": errors} if errors else None
        super().__init__(
            message=message,
            status_code=422,
            error_code=error_code,
            details=details
        )
