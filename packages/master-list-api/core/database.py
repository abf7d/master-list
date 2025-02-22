
## database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from chromadb import Client, Settings
import chromadb
from .config import settings

engine = create_engine(settings.DATABASE_URL)
# SQLite setup
# SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ChromaDB setup
# chroma_client = Client(Settings(
#     chroma_db_impl="duckdb+parquet",
#     persist_directory="./chroma_db"
# ))
# vector_collection = chroma_client.get_or_create_collection("notes_embeddings")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
