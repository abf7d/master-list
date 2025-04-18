from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid
from uuid import UUID

# Pydantic models for API
  
class NoteItem(BaseModel): # Paragraph object in the frontend
    """Request model for a single note item"""
    content: str  # Text content of the note
    id: Optional[UUID] = None  # Optional ID for the note
    # creation_tag_id: Optional[UUID] = None  # Optional tag to create under
    # sequence_number: Optional[int] = None  # Optional sequence number for ordering
    tags: List[str] = []  # List of tag IDs associated with the note
    # styles: Optional[dict] = None  # These should be specified only on the frontend and should be encoded in the content
    position: Optional[int] = None
    creation_list_id: Optional[UUID] = None  # Optional list ID to create under
    creation_type: Optional[str] = None  # Optional type of creation (e.g., 'note', 'tag')
    # level: Optional[int] = None # Tab level for indentation should be stored in conent rather than 
# Pydantic Response Models

# This needs to be updated on teh frontend because parewnt_list_type is new
class CreateNoteGroup(BaseModel):
    """Request model for creating a group of notes"""
    parent_tag_id: Optional[UUID] = None  # Optional notebook to create under
    # content: List[str]  # Full text that will be split into paragraphs
    items: List[NoteItem]  # List of note items to create 
    parent_list_type: Optional[str] = 'note'  # Optional list type for the parent tag 
    
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
    creation_list_id: Optional[UUID]
    creation_type: Optional[str]
    sequence_number: int
    tags: List[str] #List['TagResponse']

    model_config = ConfigDict(from_attributes=True)

class NoteGroupResponse(BaseModel):
    tag: TagResponse
    notes: List[NoteResponse]

    model_config = ConfigDict(from_attributes=True)

class TagButton(BaseModel):
    name: str
    # color: str
    # backgroundcolor: str

class TagCreation(TagButton):
    id: int

class TagResponse(BaseModel):
    message: Optional[str]
    error: Optional[str]
    data: TagCreation
    
class ResponseData(BaseModel):
    message: Optional[str]
    error: Optional[str]
    data: Any
    
class TagEntry(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[str]
    created_at: datetime
    order: int
    
class NoteEntry(BaseModel):
    id: UUID
    created_at: datetime
    
class NoteItemsResponse(BaseModel):
    message: Optional[str]
    error: Optional[str]
    data: Any
     