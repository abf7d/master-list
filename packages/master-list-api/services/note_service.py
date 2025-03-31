from typing import List, Optional
from uuid import UUID
import uuid
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db_init.schemas import Tag, Note, NoteTag
from models.models import CreateNoteGroup, NoteGroupResponse, NoteItemsResponse, TagEntry, TagResponse, NoteResponse
from sqlalchemy import and_
from sqlalchemy import func, case


class NoteService:
    def __init__(self, db: Session):
        self.db = db

    # def create_notes_for_tag(self, tag_id: UUID, content_list: List[str]) -> NoteGroupResponse:
    #     """
    #     Create notes under an existing tag.
        
    #     Args:
    #         tag_id: UUID of the existing parent tag
    #         content_list: List of text content for each note
            
    #     Returns:
    #         NoteGroupResponse with the tag and created notes
            
    #     Raises:
    #         NoResultFound: If the tag_id doesn't exist
    #     """
    #     # Verify tag exists
    #     tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
    #     if not tag:
    #         raise NoResultFound(f"Tag with id {tag_id} not found")
        
    #     # Create notes
    #     notes = []
    #     for i, content_item in enumerate(content_list):
    #         note = Note(
    #             content=content_item,
    #             creation_tag_id=tag_id,
    #             sequence_number=i
    #         )
    #         self.db.add(note)
    #         notes.append(note)
        
    #     self.db.flush()
        
    #     # Create note-tag associations
    #     for note in notes:
    #         note_tag = NoteTag(
    #             note_id=note.id,
    #             tag_id=tag_id
    #         )
    #         self.db.add(note_tag)
        
    #     # Commit changes
    #     self.db.commit()
        
    #     # Refresh objects from DB to get all fields
    #     for note in notes:
    #         self.db.refresh(note)
        
    #     # Construct response
    #     tag_response = TagResponse(
    #         id=tag.id,
    #         name=tag.name,
    #         parent_id=tag.parent_id,
    #         created_at=tag.created_at
    #     )
        
    #     note_responses = []
    #     for note in notes:
    #         note_responses.append(
    #             NoteResponse(
    #                 id=note.id,
    #                 content=note.content,
    #                 created_at=note.created_at,
    #                 updated_at=note.updated_at,
    #                 creation_tag_id=note.creation_tag_id,
    #                 sequence_number=note.sequence_number,
    #                 tags=[tag_response]  # Each note has the parent tag
    #             )
    #         )
        
    #     return NoteGroupResponse(
    #         tag=tag_response,
    #         notes=note_responses
    #     )
    
        
    
    def update_note_items(self, note_group: CreateNoteGroup, user_id: UUID) -> NoteGroupResponse:
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
        # Verify tag/list/note exists
        tag = self.db.query(Tag).filter(Tag.id == note_group.parent_tag_id, Tag.created_by == user_id).first()
        if not tag:
            raise NoResultFound(f"Tag with id {note_group.parent_tag_id} by {user_id} not found")
        
        # delete all of the notes with the parent_tag_id
        self.db.query(Note).filter(Note.creation_tag_id == note_group.parent_tag_id, Note.created_by == user_id).delete()
        self.db.commit()
        
        # Create notes
        notes = []
        for i, item in enumerate(note_group.items):
            note = Note(
                id=item.id,
                content=item.content,
                creation_tag_id=note_group.parent_tag_id,
                sequence_number=item.position,
                created_by=user_id
            )
            self.db.add(note)
            notes.append(note)
        
        self.db.flush()
        
        # Delete all of the NoteTag associations for the parent tag
        self.db.query(NoteTag).filter(NoteTag.tag_id == note_group.parent_tag_id, NoteTag.tag_id == note_group.parent_tag_id).delete() # NoteTag.note_id.in_([note.id for note in notes])).delete()
        
        # Create note-tag associations
        for note, item in zip(notes, note_group.items):
            note_tag = NoteTag(
                note_id=note.id,
                tag_id=note_group.parent_tag_id
            )
            self.db.add(note_tag)
            
            # assign tags to the note, need to not duplicate tags
            for tag in item.tags:
                
                #get the tag id first
                tag_obj = self.db.query(Tag).filter(Tag.name == tag.name, Tag.created_by == user_id).first()
                if not tag_obj:
                    raise NoResultFound(f"Tag with name {tag.name} by {user_id} not found")
                
                # create NoteTag if it doesn't exist
                existing_note_tag = self.db.query(NoteTag).filter(
                    NoteTag.note_id == note.id,
                    NoteTag.tag_id == tag_obj.id,
                ).first()
                if not existing_note_tag:
                    # Create a new NoteTag association
                    note_tag = NoteTag(
                        note_id=note.id,
                        tag_id=tag_obj.id
                    )
                    self.db.add(note_tag)
                
               
        
        # Commit changes
        self.db.commit()
        
        # Refresh objects from DB to get all fields
        for note in notes:
            self.db.refresh(note)
        
        # Construct response
        # tag_response = TagResponse(
        #     id=tag.id,
        #     name=tag.name,
        #     parent_id=tag.parent_id,
        #     created_at=tag.created_at
        # )
        
        # note_responses = []
        # for note in notes:
        #     note_responses.append(
        #         NoteResponse(
        #             id=note.id,
        #             content=note.content,
        #             created_at=note.created_at,
        #             updated_at=note.updated_at,
        #             creation_tag_id=note.creation_tag_id,
        #             sequence_number=note.sequence_number,
        #             tags=[tag_response]  # Each note has the parent tag
        #         )
        #     )
        
        # return NoteGroupResponse(
        #     tag=tag_response,
        #     notes=note_responses
        # )
        
        return NoteItemsResponse(
            message="Success",
            error=None,
            data='test1234'
        )

    # TODO: Move to tag repo, then call from here
    def create_tag(self, name: str, user_id:  Optional[UUID], parent_tag_id: Optional[UUID] = None) -> TagEntry:
        """
        Create a new tag with the specified name and optional parent.
        
        Args:
            name: Name for the tag
            parent_tag_id: Optional UUID of parent tag
            
        Returns:
            TagResponse for the created tag
        """
        
        # Check if a tag with this name already exists for this user
        existing_tag = self.db.query(Tag).filter(
            Tag.name == name,
            Tag.created_by == user_id
        ).first()
        
        if existing_tag:
            # Return a 409 Conflict status code with a clear message
            raise HTTPException(
                status_code=409,  # Conflict is appropriate for this case
                detail=f"A tag named '{name}' already exists for this user"
            )
        
        
        max_sequence = self.db.query(func.max(Tag.creation_order)).filter(Tag.created_by == user_id).scalar() or 0
        tag = Tag(
            name=name,
            parent_id=parent_tag_id,
            created_by=user_id,
            creation_order=max_sequence + 1
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        
        
        # todo: add id for the tag, return the same object as get tag so you can get id when creating a note
        # return TagCreation(
        # return tag.creation_order
        # return TagResponse(
        #     id=tag.id,
        #     name=tag.name,
        #     parent_id=tag.parent_id,
        #     created_at=tag.created_at
        # )
        return TagEntry(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at,
            order=tag.creation_order
        )
        
    
    #TODO Delete all of the notes_tags that are linked to tag with the id from the selecated userid and name
    #TODO: Move to tag repo
    def delete_tag(self, name: str, user_id:  Optional[UUID]) -> int:
        """
        Delete a tag with the specified ID.
        
        Args:
            tag_id: UUID of the tag to delete
            user_id: UUID of the user requesting the deletion
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            HTTPException: If tag doesn't exist or user doesn't have permission
        """
        
        # Check if a tag with this name already exists for this user
        existing_tag = self.db.query(Tag).filter(
            Tag.name == name,
            Tag.created_by == user_id
        ).first()
        
        if not existing_tag:
            # Return a 409 Conflict status code with a clear message
            raise HTTPException(
                status_code=404,  # Conflict is appropriate for this case
                detail=f"A tag named '{name}' doesn't exist for this user"
            )
        
        # Delete the tag
        self.db.delete(existing_tag)
        self.db.commit()
        
        return True
        
        
    def get_tags(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        pageSize: int = 10,
        parent_tag_id: Optional[UUID] = None
    ) -> Optional[List[TagEntry]]:
        """
        Get tags by user with optional filtering and pagination.

        Args:
            user_id: ID of the user
            query: Optional string to search tag names
            page: Page number (1-indexed)
            pageSize: Number of tags per page
            parent_tag_id: Optional UUID of parent tag

        Returns:
            A list of TagResponse models
        """

        # Base filters
        filters = [Tag.created_by == user_id]
        if parent_tag_id is not None:
            filters.append(Tag.parent_id == parent_tag_id)

        # Optional search query (e.g., for autocomplete)
        if query:
            filters.append(Tag.name.ilike(f"{query}%"))  # Starts with; for partial match use `%{query}%`

        # Query with filters and pagination
        tags_query: Query = self.db.query(Tag).filter(and_(*filters))
        
        # Need to track usage statistics: https://claude.ai/chat/5f7f1716-0dca-4db7-9d21-fcf1de0c92a6
        tags_query = tags_query.order_by(
            case((Tag.name == query, 1), else_=0).desc(),
            func.length(Tag.name),
            Tag.name.asc()
        )  # Optional ordering
        tags_query = tags_query.offset((page - 1) * pageSize).limit(pageSize)

        tags = tags_query.all()

        tag_responses = []
        for tag in tags:
            
            tag_responses.append(
                TagEntry(
                    id=tag.id,
                    name=tag.name,
                    parent_id=tag.parent_id,
                    created_at=tag.created_at,
                    order=tag.creation_order
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