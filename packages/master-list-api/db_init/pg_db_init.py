from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Tag, Note, NoteTag  # Import the models from your models.py
from ..core import settings

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

# from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, Integer, UniqueConstraint
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker
# import uuid
# from datetime import datetime
# from config import settings

# # Create the base class
# Base = declarative_base()

# # Define the models
# class Tag(Base):
#     __tablename__ = "tags"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     name = Column(String(50), index=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     parent_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=True)
    
#     __table_args__ = (
#         UniqueConstraint('name', 'parent_id', name='uix_tag_name_parent'),
#     )
    
#     # Relationships
#     parent = relationship("Tag", remote_side=[id], back_populates="children")
#     children = relationship("Tag", back_populates="parent")
#     notes = relationship("Note", secondary="note_tags", back_populates="tags")
#     created_notes = relationship("Note", back_populates="creation_tag")

# class Note(Base):
#     __tablename__ = "notes"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     content = Column(Text)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     creation_tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=False)
#     sequence_number = Column(Integer)
    
#     # Relationships
#     tags = relationship("Tag", secondary="note_tags", back_populates="notes")
#     creation_tag = relationship("Tag", foreign_keys=[creation_tag_id], back_populates="created_notes")

# class NoteTag(Base):
#     __tablename__ = "note_tags"
    
#     note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id'), primary_key=True)
#     tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)

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