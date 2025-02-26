from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid
from uuid import UUID

# Pydantic models for API
class CreateNoteGroup(BaseModel):
    """Request model for creating a group of notes"""
    parent_tag_id: Optional[UUID] = None  # Optional notebook to create under
    content: List[str]  # Full text that will be split into paragraphs

# Pydantic Response Models
class TagResponse(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NoteResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    updated_at: datetime
    creation_tag_id: UUID
    sequence_number: int
    tags: List['TagResponse']

    model_config = ConfigDict(from_attributes=True)

class NoteGroupResponse(BaseModel):
    tag: TagResponse
    notes: List[NoteResponse]

    model_config = ConfigDict(from_attributes=True)