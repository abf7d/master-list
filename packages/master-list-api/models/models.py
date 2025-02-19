from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    parent_id = Column(UUID, ForeignKey('tags.id'), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', name='uix_tag_name_parent'),
    )
    
    # Relationships
    parent = relationship("Tag", remote_side=[id], back_populates="children")
    children = relationship("Tag", back_populates="parent")
    notes = relationship("Note", secondary="note_tags", back_populates="tags")
    created_notes = relationship("Note", back_populates="creation_tag")  # Notes created under this tag

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    content = Column(Text)  # Single paragraph of content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creation_tag_id = Column(UUID, ForeignKey('tags.id'), nullable=False)  # Tag under which this note was created
    sequence_number = Column(Integer)  # Order within the original creation group
    
    # Relationships
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")
    creation_tag = relationship("Tag", back_populates="created_notes")

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    note_id = Column(UUID, ForeignKey('notes.id'), primary_key=True)
    tag_id = Column(UUID, ForeignKey('tags.id'), primary_key=True)

# Pydantic models for API
class CreateNoteGroup(BaseModel):
    """Request model for creating a group of notes"""
    tag_name: str
    parent_tag_id: Optional[UUID] = None  # Optional notebook to create under
    content: str  # Full text that will be split into paragraphs

# Pydantic Response Models
class TagResponse(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NoteResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    updated_at: datetime
    creation_tag_id: UUID
    sequence_number: int
    tags: List[TagResponse]

    class Config:
        from_attributes = True

class NoteGroupResponse(BaseModel):
    tag: TagResponse
    notes: List[NoteResponse]

    class Config:
        from_attributes = True





# ## models.py
# from datetime import datetime
# from typing import Optional, List
# from pydantic import BaseModel, Field
# from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# Base = declarative_base()

# from sqlalchemy.dialects.postgresql import UUID
# from uuid import uuid4

# from sqlalchemy.types import TypeDecorator, CHAR
# from sqlalchemy.dialects.postgresql import UUID
# import uuid

# class GUID(TypeDecorator):
#     """Platform-independent GUID type.
#     Uses PostgreSQL's UUID type, otherwise uses
#     CHAR(32), storing as stringified hex values.
#     """
#     impl = CHAR
#     cache_ok = True

#     def load_dialect_impl(self, dialect):
#         if dialect.name == 'postgresql':
#             return dialect.type_descriptor(UUID())
#         else:
#             return dialect.type_descriptor(CHAR(32))

#     def process_bind_param(self, value, dialect):
#         if value is None:
#             return value
#         elif dialect.name == 'postgresql':
#             return str(value)
#         else:
#             if not isinstance(value, uuid.UUID):
#                 return "%.32x" % uuid.UUID(value).int
#             else:
#                 # hexstring
#                 return "%.32x" % value.int

#     def process_result_value(self, value, dialect):
#         if value is None:
#             return value
#         else:
#             if not isinstance(value, uuid.UUID):
#                 value = uuid.UUID(value)
#             return value
        

# class NoteDB(Base):
#     __tablename__ = "notes"
    
#     id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
#     title = Column(String(255))
#     content = Column(Text)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     tags = Column(String(255))  # Store as comma-separated values

# class NoteCreate(BaseModel):
#     title: str
#     content: str
#     tags: Optional[List[str]] = []

# class NoteResponse(BaseModel):
#     id: UUID
#     title: str
#     content: str
#     tags: List[str]
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True