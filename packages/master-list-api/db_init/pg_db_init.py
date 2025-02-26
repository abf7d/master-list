from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas import Base, Tag, Note, NoteTag  # Use absolute import

# Only import the SQLAlchemy models, not the Pydantic models
# If you need settings, import only what you need
from core.config import settings

def init_db():
    """Initialize the database and create all tables"""
    # Create engine
    engine = create_engine(
        settings.DATABASE_URL,
        echo=True  # Set to False in production
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create engine and SessionLocal at module level
engine, SessionLocal = init_db()

if __name__ == "__main__":
    # Example usage
    print(f"Initializing database with URL: {settings.DATABASE_URL}")
    
    # Create a test session
    db = SessionLocal()
    
    try:
        # Create a test tag
        test_tag = Tag(name="Test Notebook")
        db.add(test_tag)
        db.commit()
        
        print(f"Created test tag with ID: {test_tag.id}")
        
        # Query to verify
        tags = db.query(Tag).all()
        for tag in tags:
            print(f"Tag: {tag.name}")
            
    finally:
        db.close()

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from models.models import Base, Tag, Note, NoteTag  # Import the models from your models.py
# from core.config import settings

# def init_db():
#     """Initialize the database and create all tables"""
#     # Create engine
#     engine = create_engine(
#         settings.DATABASE_URL,
#         echo=True  # Set to False in production
#     )
    
#     # Create all tables
#     Base.metadata.create_all(engine)
    
#     # Create sessionmaker
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
#     return engine, SessionLocal

# def get_db():
#     """Dependency to get DB session"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Create engine and SessionLocal at module level
# engine, SessionLocal = init_db()

# if __name__ == "__main__":
#     # Example usage
#     print(f"Initializing database with URL: {settings.DATABASE_URL}")
    
#     # Create a test session
#     db = SessionLocal()
    
#     try:
#         # Create a test tag
#         test_tag = Tag(name="Test Notebook")
#         db.add(test_tag)
#         db.commit()
        
#         print(f"Created test tag with ID: {test_tag.id}")
        
#         # Query to verify
#         tags = db.query(Tag).all()
#         for tag in tags:
#             print(f"Tag: {tag.name}")
            
#     finally:
#         db.close()
