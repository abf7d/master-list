
# app/exceptions/handlers.py
import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from exceptions.custom_exceptions import APIError
from models.error_models import ErrorResponse, ErrorDetail
from exceptions.registry import registry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@registry.handler_for(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler for FastAPI's built-in HTTPException.
    Maps status codes to standard error codes and formats the response.
    """
    # Map common status codes to error codes
    status_to_code = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
    }
    
    error_code = status_to_code.get(exc.status_code, f"HTTP_{exc.status_code}")
    
    # Log the error
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    
    # Get additional details if available
    details = getattr(exc, "details", None)
    
    # Convert the exception to our standard error response
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            error_code=error_code,
            details=details
        ).dict(exclude_none=True)
    )
    
@registry.handler_for(APIError)
async def api_exception_handler(request: Request, exc: APIError):
    """Handle all custom API exceptions"""
    logger.error(f"API error: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details
        ).dict(exclude_none=True)
    )

@registry.handler_for(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors from request bodies, query params, etc."""
    error_details = []
    for error in exc.errors():
        error_details.append(ErrorDetail(
            loc=error.get("loc"),
            msg=error.get("msg"),
            type=error.get("type")
        ))
    
    logger.error(f"Validation error: {error_details}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            errors=error_details
        ).dict(exclude_none=True)
    )

@registry.default_handler()
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for any unhandled exceptions"""
    logger.exception("Unhandled exception occurred")
    
    # In production, don't return the actual error message
    # to avoid leaking sensitive information
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR",
        ).dict(exclude_none=True)
    )

# Create an enhanced HTTPException with additional context
class EnhancedHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.details = details

# Register a handler for the enhanced exception
@registry.handler_for(EnhancedHTTPException)
async def enhanced_http_exception_handler(request: Request, exc: EnhancedHTTPException):
    """Handler for enhanced HTTP exceptions with additional context"""
    logger.error(f"Enhanced HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            error_code=exc.error_code or f"HTTP_{exc.status_code}",
            details=exc.details
        ).dict(exclude_none=True)
    )
    
    
    
# # Example error handling exception handling routes demonstrating exceptions
# @app.get("/users/{user_id}")
# async def get_user(user_id: int):
#     if user_id <= 0:
#         # You could create a custom ValidationError class, but for
#         # demonstration we'll use FastAPI's built-in validation
#         pass
    
#     if user_id == 999:
#         raise DatabaseError("Failed to connect to the user database")
    
#     if user_id == 888:
#         raise AuthenticationError("Invalid or expired token")
    
#     if user_id == 777:
#         raise ForbiddenError("Not authorized to view this user profile")
    
#     if user_id > 1000:
#         raise NotFoundError(f"User with ID {user_id} not found")
    
#     # Success case
#     return {"user_id": user_id, "name": "John Doe", "email": "john@example.com"}

# @app.get("/test-error")
# async def test_generic_error():
#     # This will trigger the generic exception handler
#     1 / 0
#     return {"message": "This will never be returned"}