from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session


from db_init.schemas import Note
from models.models import NoteCreation, NoteEntry, TagEntry
from sqlalchemy import and_, select, delete, tuple_, update
from sqlalchemy import func, case
from .util_service import UtilService

class NoteService:
    def __init__(self, db: Session):
        self.db = db
        self.utils = UtilService(db)
        
    
    
    def create_note(self, user_id:  Optional[UUID]) -> TagEntry:
        """
        Create a new note with.
        
        Args:
            name: Name for the tag
            parent_tag_id: Optional UUID of parent tag
            
        Returns:
            TagResponse for the created tag
        """
        
        note = Note(
            created_by=user_id,
            
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return NoteCreation( # TODO: Change to NoteEntry
            id=note.id,
            created_at=note.created_at,
        )
    
    
    def delete_note(self, note_id: UUID, user_id:  Optional[UUID]) -> int:
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
        existing_note = self.db.query(Note).filter(
            Note.id == note_id,
            Note.created_by == user_id
        ).first()
        
        if not existing_note:
            # Return a 409 Conflict status code with a clear message
            raise HTTPException(
                status_code=404,  # Conflict is appropriate for this case
                detail=f"A note named '{note_id}' doesn't exist for this user"
            )
        
        # Delete the tag
        self.db.delete(existing_note)
        self.db.commit()
        
        return True
        
    
    def get_notes(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        pageSize: int = 10,
        id: Optional[str] = None,
        parent_tag_id: Optional[UUID] = None
    ) -> Optional[List[TagEntry]]:
            """
            Get notes by user with optional filtering and pagination.

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
            filters = [Note.created_by == user_id]
            
            if id:
                filters.append(Note.id == id)

            # Optional search query (e.g., for autocomplete)
            if query:
                filters.append(Note.title.ilike(f"{query}%"))  # Starts with; for partial match use `%{query}%`

            # Query with filters and pagination
            notes_query: Query = self.db.query(Note).filter(and_(*filters))
            
            # Sort based on query presence
            if query:
                notes_query = notes_query.order_by(
                    case((Note.title == query, 1), else_=0).desc(),
                    func.length(Note.title),
                    Note.created_at.desc(),
                )
            else:
                notes_query = notes_query.order_by(Note.updated_at.desc())
            notes_query = notes_query.offset((page - 1) * pageSize).limit(pageSize)

            notes = notes_query.all()

            # Get all note IDs
            note_ids = [note.id for note in notes]
            
            # Using a window function to limit to top 2 NoteItems per note
            # This requires using raw SQL with the func module
            from sqlalchemy import func, text
            from sqlalchemy.orm import aliased

            # First, create a subquery that ranks NoteItems for each note
            ranked_items = text("""
                SELECT 
                    list_id, 
                    note_item_id, 
                    content,
                    ROW_NUMBER() OVER (PARTITION BY list_id ORDER BY sequence_number) as row_num
                FROM note_item_lists
                JOIN note_items ON note_item_lists.note_item_id = note_items.id
                WHERE 
                    list_id IN :note_ids AND
                    list_type = 'note' AND
                    note_items.created_by = :user_id
            """)
            
            # Then, select only rows where row_num <= 2
            top_items_query = text("""
                SELECT list_id, content
                FROM (
                    SELECT 
                        list_id, 
                        note_item_id, 
                        content,
                        ROW_NUMBER() OVER (PARTITION BY list_id ORDER BY sequence_number) as row_num
                    FROM note_item_lists
                    JOIN note_items ON note_item_lists.note_item_id = note_items.id
                    WHERE 
                        list_id IN :note_ids AND
                        list_type = 'note' AND
                        note_items.created_by = :user_id
                ) as ranked
                WHERE row_num <= 2
                ORDER BY list_id, row_num
            """)
            
            # Execute the query with parameters
            note_items_result = self.db.execute(
                top_items_query, 
                {"note_ids": tuple(note_ids) if note_ids else ('00000000-0000-0000-0000-000000000000',), 
                "user_id": user_id}
            ).fetchall()
            
            # Group NoteItems by note_id
            note_items_map = {}
            for list_id, content in note_items_result:
                if list_id not in note_items_map:
                    note_items_map[list_id] = []
                note_items_map[list_id].append(content)
            
            note_responses = []
            for i, note in enumerate(notes):
                # Get first 2 NoteItems for description
                description = note.description
                if not description and note.id in note_items_map:
                    # Items are already limited to 2 by the query
                    items = note_items_map[note.id]
                     # Check if there are any items
                    if len(items) > 0 and (len(items) == 1 and not items[0]) == False:
                        # Truncate each item if it's too long
                        truncated_items = [item[:100] + "..." if len(item) > 100 else item for item in items]
                        
                        # Format as HTML unordered list
                        list_items = "".join([f"<li>{item}</li>" for item in truncated_items])
                        description = f"<ul>{list_items}</ul>"
                    else:
                        # No items found, set description to None/null
                        description = None
                max_page = self.utils.get_max_page(note.id, 'note')
                note_responses.append(
                    NoteEntry(
                        id=note.id,
                        title=note.title,
                        description=description,
                        created_at=note.created_at,
                        updated_at=note.updated_at,
                        order=i,
                        max_page=max_page,
                    )
                )
            
            return note_responses

