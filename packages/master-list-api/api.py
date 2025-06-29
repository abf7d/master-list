from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler
import logging
import uvicorn 
import os

from exceptions.registry import registry
from fastapi.exceptions import RequestValidationError
from exceptions.handlers import (
    api_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from exceptions.custom_exceptions import (
    APIError,
    NotFoundError,
    DatabaseError,
    AuthenticationError,
    ForbiddenError,
    ValidationError
)

# Make sure the logs directory exists
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create a logger
logger = logging.getLogger('main-list api')
logger.setLevel(logging.INFO)

# Create handlers with path to logs folder
log_file_path = os.path.join(logs_dir, "app.log")
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10485760,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

from routes import (tag_routes, note_routes, item_routes, overview, account_routes) #(notes_routes, account_routes) #, tags_routes

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
# Apply all handlers to the app
registry.apply_to_app(app)

# Middleware for request logging
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        # Exceptions will be handled by the exception handlers
        # This just ensures they're logged at the middleware level
        logger.error(f"Request failed: {str(e)}")
        raise


# app.include_router(notes_routes.router)
app.include_router(tag_routes.router)
app.include_router(note_routes.router)
app.include_router(item_routes.router)
app.include_router(overview.router)
app.include_router(account_routes.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    # Initialize resources, connect to database, etc.

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
    
if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="info", reload=True)