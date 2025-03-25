from fastapi import FastAPI
from typing import Dict, Type, Callable, Any
import inspect
import logging

logger = logging.getLogger(__name__)

class ExceptionRegistry:
    """A registry for mapping exception types to their handlers."""
    
    def __init__(self):
        self.handlers: Dict[Type[Exception], Callable] = {}
    
    def register(self, exc_type: Type[Exception], handler: Callable) -> None:
        """Register a handler for a specific exception type."""
        self.handlers[exc_type] = handler
        logger.debug(f"Registered handler for {exc_type.__name__}")
    
    def handler_for(self, exc_type: Type[Exception]):
        """Decorator to register a handler for an exception type."""
        def decorator(handler_func):
            self.register(exc_type, handler_func)
            return handler_func
        return decorator
    
    def default_handler(self):
        """Decorator to register a handler for the base Exception class."""
        return self.handler_for(Exception)
    
    def apply_to_app(self, app: FastAPI) -> None:
        """Apply all registered handlers to a FastAPI application."""
        for exc_type, handler in self.handlers.items():
            app.add_exception_handler(exc_type, handler)
            logger.info(f"Added exception handler for {exc_type.__name__} to FastAPI app")

# Create a global registry instance
registry = ExceptionRegistry()