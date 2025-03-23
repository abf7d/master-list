from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler
import logging
import uvicorn 

# Configure the logger with rotation
handler = RotatingFileHandler(
    "app.log", 
    maxBytes=10485760,  # 10MB
    backupCount=5       # Keep up to 5 backup files
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('list.api')


# from .models import NoteDB, NoteCreate, NoteResponse
# from .database import get_db, engine

from routes import (notes_routes, account_routes) #, tags_routes

# Create PostgreSQL tables
# NoteDB.metadata.create_all(bind=engine)

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes_routes.router)
app.include_router(account_routes.router)

if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="info", reload=True)