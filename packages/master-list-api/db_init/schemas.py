import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    oauth_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)  
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), index=True)
    # Used for color mapping
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
    
    # Define note_items relationship through the junction table
    note_items = relationship(
        "NoteItem",
        secondary="note_item_lists",
        primaryjoin="Tag.id == NoteItemList.list_id",
        secondaryjoin="and_(NoteItem.id == NoteItemList.note_item_id, NoteItemList.list_type == 'tag')",
        back_populates="tags",
        viewonly=True
    )

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_by_user = relationship("User")
    
    # Define note_items relationship through the junction table
    note_items = relationship(
        "NoteItem",
        secondary="note_item_lists",
        primaryjoin="Note.id == NoteItemList.list_id",
        secondaryjoin="and_(NoteItem.id == NoteItemList.note_item_id, NoteItemList.list_type == 'note')",
        back_populates="notes",
        viewonly=True
    )

class NoteItemList(Base):
    __tablename__ = "note_item_lists"
    
    note_item_id = Column(UUID(as_uuid=True), ForeignKey('note_items.id'), primary_key=True)
    list_id = Column(UUID(as_uuid=True), primary_key=True)  # Renamed from tag_id to list_id for clarity
    list_type = Column(String(4), nullable=False)  # 'tag' or 'note'
    is_origin = Column(Boolean, default=False)  # Fixed Boolean type
    sort_order = Column(Integer, nullable=True)
    page = Column(Integer, nullable=True)
    __table_args__ = (
        CheckConstraint(list_type.in_(['tag', 'note']), name='check_list_type'),
        Index('idx_list_id_type', list_id, list_type), 
    )
    
    # We can't define proper foreign keys for list_id since it could refer to either table
    # This is a limitation of the polymorphic association approach

class NoteItem(Base):
    __tablename__ = "note_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.oauth_id'), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sequence_number = Column(Integer)
    
    created_by_user = relationship("User")
    
    # Relationships to containing lists
    tags = relationship(
        "Tag",
        secondary="note_item_lists",
        primaryjoin="NoteItem.id == NoteItemList.note_item_id",
        secondaryjoin="and_(Tag.id == NoteItemList.list_id, NoteItemList.list_type == 'tag')",
        back_populates="note_items"
    )
    
    notes = relationship(
        "Note",
        secondary="note_item_lists",
        primaryjoin="NoteItem.id == NoteItemList.note_item_id",
        secondaryjoin="and_(Note.id == NoteItemList.list_id, NoteItemList.list_type == 'note')",
        back_populates="note_items"
    )
    