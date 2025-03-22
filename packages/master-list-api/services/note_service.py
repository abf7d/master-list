from typing import List, Optional
from uuid import UUID
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db_init.schemas import Tag, Note, NoteTag
from models.models import CreateNoteGroup, NoteGroupResponse, TagResponse, NoteResponse
from sqlalchemy import and_

class NoteService:
    def __init__(self, db: Session):
        self.db = db

    def create_notes_for_tag(self, tag_id: UUID, content_list: List[str]) -> NoteGroupResponse:
        """
        Create notes under an existing tag.
        
        Args:
            tag_id: UUID of the existing parent tag
            content_list: List of text content for each note
            
        Returns:
            NoteGroupResponse with the tag and created notes
            
        Raises:
            NoResultFound: If the tag_id doesn't exist
        """
        # Verify tag exists
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise NoResultFound(f"Tag with id {tag_id} not found")
        
        # Create notes
        notes = []
        for i, content_item in enumerate(content_list):
            note = Note(
                content=content_item,
                creation_tag_id=tag_id,
                sequence_number=i
            )
            self.db.add(note)
            notes.append(note)
        
        self.db.flush()
        
        # Create note-tag associations
        for note in notes:
            note_tag = NoteTag(
                note_id=note.id,
                tag_id=tag_id
            )
            self.db.add(note_tag)
        
        # Commit changes
        self.db.commit()
        
        # Refresh objects from DB to get all fields
        for note in notes:
            self.db.refresh(note)
        
        # Construct response
        tag_response = TagResponse(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at
        )
        
        note_responses = []
        for note in notes:
            note_responses.append(
                NoteResponse(
                    id=note.id,
                    content=note.content,
                    created_at=note.created_at,
                    updated_at=note.updated_at,
                    creation_tag_id=note.creation_tag_id,
                    sequence_number=note.sequence_number,
                    tags=[tag_response]  # Each note has the parent tag
                )
            )
        
        return NoteGroupResponse(
            tag=tag_response,
            notes=note_responses
        )

    def create_tag(self, name: str, user_id:  Optional[UUID], parent_tag_id: Optional[UUID] = None) -> TagResponse:
        """
        Create a new tag with the specified name and optional parent.
        
        Args:
            name: Name for the tag
            parent_tag_id: Optional UUID of parent tag
            
        Returns:
            TagResponse for the created tag
        """
        tag = Tag(
            name=name,
            parent_id=parent_tag_id,
            user_id=user_id
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        
        return TagResponse(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at
        )
    def get_tags(self, user_id: str, parent_tag_id: Optional[UUID] = None) -> Optional[List[TagResponse]]:
        """
        Create a new tag with the specified name and optional parent.
        
        Args:
            name: Name for the tag
            parent_tag_id: Optional UUID of parent tag
            
        Returns:
            TagResponse for the created tag
        """

        tags = self.db.query(Tag).filter(and_(Tag.parent_id == parent_tag_id, Tag.created_by == user_id))

        tag_responses = []
        for tag in tags:
            tag_responses.append(
                TagResponse(
                    id=tag.id,
                    name=tag.name,
                    parent_id=tag.parent_id,
                    created_at=tag.created_at
                )
            )
        
        return tag_responses

    def get_note_group_by_tag_id(self, tag_id: UUID) -> Optional[NoteGroupResponse]:
        """
        Get a note group by tag ID
        
        Args:
            tag_id: UUID of the tag
            
        Returns:
            NoteGroupResponse or None if tag not found
        """
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None
            
        notes = self.db.query(Note).filter(Note.creation_tag_id == tag_id).order_by(Note.sequence_number).all()
        
        tag_response = TagResponse(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at
        )
        
        note_responses = []
        for note in notes:
            note_responses.append(
                NoteResponse(
                    id=note.id,
                    content=note.content,
                    created_at=note.created_at,
                    updated_at=note.updated_at,
                    creation_tag_id=note.creation_tag_id,
                    sequence_number=note.sequence_number,
                    tags=[tag_response]
                )
            )
            
        return NoteGroupResponse(
            tag=tag_response,
            notes=note_responses
        )
        
    def update_tag_name(self, tag_id: UUID, new_name: str) -> TagResponse:
        """
        Update the name of an existing tag
        
        Args:
            tag_id: UUID of the tag to update
            new_name: New name for the tag
            
        Returns:
            Updated TagResponse
            
        Raises:
            NoResultFound: If the tag_id doesn't exist
        """
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise NoResultFound(f"Tag with id {tag_id} not found")
            
        tag.name = new_name
        self.db.commit()
        self.db.refresh(tag)
        
        return TagResponse(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at
        )

# from fastapi import Depends
# from repos.notes_repo import NoteRepo
# from db_init.schemas import NoteCreate

# class NotesService:
#     def __init__(self, repo: NoteRepo = Depends()):
#         self.repo = repo
    
#     async def create_order(self, order: NoteCreate):
#         # Business logic, validation, etc.
#         return await self.repo.create(order)