from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn 

#ask chatgpt about logger, test writing some logs
""" Initialize the logger """
logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("plots.api")


# from .models import NoteDB, NoteCreate, NoteResponse
# from .database import get_db, engine

from routes import (notes_routes) #, tags_routes

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

if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="info", reload=True)