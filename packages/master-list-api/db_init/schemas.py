from sqlalchemy import CheckConstraint, Column, String, Text, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, object_session
from datetime import datetime
import uuid

# SQLAlchemy Base
Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     oauth_id = Column(UUID(as_uuid=True), unique=True, nullable=False)  
#     email = Column(String(255), unique=True, nullable=False)  # Unique user lookup
#     name = Column(String(255), unique=True, nullable=False)  
#     created_at = Column(DateTime, default=datetime.utcnow)

# class Tag(Base):
#     __tablename__ = "tags"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     name = Column(String(50), index=True)
#     # For color indexing
#     creation_order = Column(Integer, nullable=False, default=0) #for color indexing
#     created_at = Column(DateTime, default=datetime.utcnow)
#     created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)  # Owner of the tag
#     parent_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=True)

#     __table_args__ = (
#         UniqueConstraint('name', 'parent_id', name='uix_tag_name_parent'),
#     )
    
#     # Relationships
#     parent = relationship("Tag", remote_side=[id], back_populates="children")
#     children = relationship("Tag", back_populates="parent")
#     # notes = relationship("NoteItem", secondary="note_item_tags", back_populates="tags")
#     # created_notes = relationship("NoteItem", back_populates="creation_tag")
#     created_by_user = relationship("User")  # Track the owner
    
#     # Relationship for tags assigned to note items
#     note_items = relationship(
#         "NoteItem",
#         secondary="note_item_tags",
#         primaryjoin="Tag.id == NoteItemTag.tag_id",
#         secondaryjoin="NoteItem.id == NoteItemTag.note_item_id"
#     )
    
#     # Get note items where this tag is the origin
#     @property
#     def origin_items(self):
#         from sqlalchemy.orm import object_session
#         session = object_session(self)
#         return session.query(NoteItem).filter(
#             NoteItem.origin_id == self.id,
#             NoteItem.origin_type == 'tag'
#         ).all()

# class Note(Base):
#     __tablename__ = "notes"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     title = Column(String(255), nullable=True)
#     description = Column(Text, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)  # Owner of the note
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     created_by_user = relationship("User")
#     @property
#     def note_items(self):
#         from sqlalchemy.orm import object_session
#         session = object_session(self)
#         return session.query(NoteItem).filter(
#             NoteItem.origin_id == self.id,
#             NoteItem.origin_type == 'note'
#         ).all()
        
# class NoteItemTag(Base):
#     __tablename__ = "note_item_tags"
    
#     note_item_id = Column(UUID(as_uuid=True), ForeignKey('note_items.id'), primary_key=True)
#     tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)
#     origin_tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=True)
#     origin_type = Column(String(4), nullable=False) 
    
#     # Define relationships explicitly
#     # tag = relationship("Tag", foreign_keys=[tag_id])
#     # origin_tag = relationship("Tag", foreign_keys=[origin_tag_id])
#     # note_item = relationship("NoteItem", foreign_keys=[note_item_id])
    
# class NoteItem(Base):
#     __tablename__ = "note_items"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     content = Column(Text)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)  # Owner of the note
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     # creation_tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=False)
#     origin_id = Column(UUID(as_uuid=True), nullable=False)  # Can reference either tags.id or notes.id
#     origin_type = Column(String(4), nullable=False)  
       
#     sequence_number = Column(Integer)
#      # Many-to-many relationship with tags
#     tags = relationship(
#         "Tag",
#         secondary="note_item_tags",
#         primaryjoin="NoteItem.id == NoteItemTag.note_item_id",
#         secondaryjoin="Tag.id == NoteItemTag.tag_id"
#     )
    
#     # Polymorphic relationship to either Tag or Note
#     @property
#     def origin(self):
#         if self.origin_type == 'tag':
#             from sqlalchemy.orm import object_session
#             session = object_session(self)
#             return session.query(Tag).filter(Tag.id == self.origin_id).first()
#         elif self.origin_type == 'note':
#             from sqlalchemy.orm import object_session
#             session = object_session(self)
#             return session.query(Note).filter(Note.id == self.origin_id).first()
#         return None
    
#     __table_args__ = (
#         CheckConstraint(origin_type.in_(['tag', 'note']), name='check_origin_type'),
#     )
   
    
#     # Relationships
#     tags = relationship("Tag", secondary="note_item_tags", back_populates="notes")
#     # creation_tag = relationship("Tag", back_populates="created_notes")
#     # creation_tag = relationship("Tag", back_populates="created_notes")
#     created_by_user = relationship("User") 


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    oauth_id = Column(UUID(as_uuid=True), unique=True, nullable=False)  
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), index=True)
    creation_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), nullable=True)

    __table_args__ = (
        UniqueConstraint('name', 'parent_id', name='uix_tag_name_parent'),
    )
    
    # Relationships
    parent = relationship("Tag", remote_side=[id], back_populates="children")
    children = relationship("Tag", back_populates="parent")
    created_by_user = relationship("User")
    
    # Define note_items relationship with explicit foreign keys
    note_items = relationship(
        "NoteItem",
        secondary="note_item_tags",
        primaryjoin="Tag.id == NoteItemTag.tag_id",
        secondaryjoin="NoteItem.id == NoteItemTag.note_item_id",
        back_populates="tags"
    )
    
    # Property for origin items
    @property
    def origin_items(self):
        from sqlalchemy.orm import object_session
        session = object_session(self)
        return session.query(NoteItem).filter(
            NoteItem.origin_id == self.id,
            NoteItem.origin_type == 'tag'
        ).all()

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_by_user = relationship("User")
    
    @property
    def note_items(self):
        from sqlalchemy.orm import object_session
        session = object_session(self)
        return session.query(NoteItem).filter(
            NoteItem.origin_id == self.id,
            NoteItem.origin_type == 'note'
        ).all()

class NoteItemTag(Base):
    __tablename__ = "note_item_tags"
    
    note_item_id = Column(UUID(as_uuid=True), ForeignKey('note_items.id'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)
    # Removed the origin_tag_id column to simplify
    origin_type = Column(String(4), nullable=False)

class NoteItem(Base):
    __tablename__ = "note_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    origin_id = Column(UUID(as_uuid=True), nullable=False)
    origin_type = Column(String(4), nullable=False)
    sequence_number = Column(Integer)
    
    # Define a SINGLE tags relationship with explicit primaryjoin/secondaryjoin
    tags = relationship(
        "Tag",
        secondary="note_item_tags",
        primaryjoin="NoteItem.id == NoteItemTag.note_item_id",
        secondaryjoin="Tag.id == NoteItemTag.tag_id",
        back_populates="note_items"
    )
    
    created_by_user = relationship("User")
    
    @property
    def origin(self):
        if self.origin_type == 'tag':
            from sqlalchemy.orm import object_session
            session = object_session(self)
            return session.query(Tag).filter(Tag.id == self.origin_id).first()
        elif self.origin_type == 'note':
            from sqlalchemy.orm import object_session
            session = object_session(self)
            return session.query(Note).filter(Note.id == self.origin_id).first()
        return None
    
    __table_args__ = (
        CheckConstraint(origin_type.in_(['tag', 'note']), name='check_origin_type'),
    )
    
    # tags = relationship(
    #     "Tag",
    #     secondary=lambda: NoteItemTag.__table__,
    #     primaryjoin=lambda: NoteItem.id == NoteItemTag.__table__.c.note_item_id,
    #     secondaryjoin=lambda: Tag.id == NoteItemTag.__table__.c.tag_id,
    #     back_populates="notes"
    # )
    # @property
    # def origin(self):
    #     if self.origin_type == 'tag':
    #         return object_session(self).query(Tag).filter(Tag.id == self.origin_id).first()
    #     elif self.origin_type == 'note':
    #         return object_session(self).query(Note).filter(Note.id == self.origin_id).first()
    #     return None


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



