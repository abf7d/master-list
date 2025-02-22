from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# SQLAlchemy Base
Base = declarative_base()

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', name='uix_tag_name_parent'),
    )
    
    # Relationships
    parent = relationship("Tag", remote_side=[id], back_populates="children")
    children = relationship("Tag", back_populates="parent")
    notes = relationship("Note", secondary="note_tags", back_populates="tags")
    created_notes = relationship("Note", back_populates="creation_tag")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creation_tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=False)
    sequence_number = Column(Integer)
    
    # Relationships
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")
    creation_tag = relationship("Tag", back_populates="created_notes")

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)

# from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
# from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import UUID
# import uuid
# from datetime import datetime
# from typing import List, Optional
# from pydantic import BaseModel


# from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from sqlalchemy import UniqueConstraint
# from datetime import datetime
# import uuid
# from typing import List, Optional, Dict
# from pydantic import BaseModel
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class Tag(Base):
#     __tablename__ = "tags"
    
#     id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
#     name = Column(String(50), index=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     parent_id = Column(UUID, ForeignKey('tags.id'), nullable=True)
    
#     __table_args__ = (
#         UniqueConstraint('name', 'parent_id', name='uix_tag_name_parent'),
#     )
    
#     # query chatgpt and ask what this does
#     # Relationships
#     parent = relationship("Tag", remote_side=[id], back_populates="children")
#     children = relationship("Tag", back_populates="parent")
#     notes = relationship("Note", secondary="note_tags", back_populates="tags")
#     created_notes = relationship("Note", back_populates="creation_tag")  # Notes created under this tag

# class Note(Base):
#     __tablename__ = "notes"
    
#     id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
#     content = Column(Text)  # Single paragraph of content
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     creation_tag_id = Column(UUID, ForeignKey('tags.id'), nullable=False)  # Tag under which this note was created
#     sequence_number = Column(Integer)  # Order within the original creation group
    
#     # Relationships
#     tags = relationship("Tag", secondary="note_tags", back_populates="notes")
#     creation_tag = relationship("Tag", back_populates="created_notes")

# class NoteTag(Base):
#     __tablename__ = "note_tags"
    
#     note_id = Column(UUID, ForeignKey('notes.id'), primary_key=True)
#     tag_id = Column(UUID, ForeignKey('tags.id'), primary_key=True)

# # Pydantic models for API
# class CreateNoteGroup(BaseModel):
#     """Request model for creating a group of notes"""
#     tag_name: str
#     parent_tag_id: Optional[UUID] = None  # Optional notebook to create under
#     content: str  # Full text that will be split into paragraphs

# # Pydantic Response Models
# class TagResponse(BaseModel):
#     id: UUID
#     name: str
#     parent_id: Optional[UUID]
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# class NoteResponse(BaseModel):
#     id: UUID
#     content: str
#     created_at: datetime
#     updated_at: datetime
#     creation_tag_id: UUID
#     sequence_number: int
#     tags: List[TagResponse]

#     class Config:
#         from_attributes = True

# class NoteGroupResponse(BaseModel):
#     tag: TagResponse
#     notes: List[NoteResponse]

#     class Config:
#         from_attributes = True



