from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from typing import List
from db_init.schemas import Note, Tag
from models.models import CreateNoteGroup, NoteGroupResponse, NoteResponse, TagResponse

class NoteRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_note_group(self, note_group: CreateNoteGroup) -> NoteGroupResponse:
        # Create the tag that will group these notes
        tag = Tag(
            name=note_group.tag_name,
            parent_id=note_group.parent_tag_id
        )
        self.db.add(tag)
        self.db.flush()  # Get the tag ID
        
        # Split content into paragraphs and create note entries
        paragraphs = [p.strip() for p in note_group.content.split('\n\n') if p.strip()]
        notes = []
        
        for idx, paragraph in enumerate(paragraphs):
            note = Note(
                content=paragraph,
                creation_tag_id=tag.id,
                sequence_number=idx,
                tags=[tag]  # Automatically associate with creation tag
            )
            notes.append(note)
            
        self.db.add_all(notes)
        self.db.commit()
        
        return NoteGroupResponse(
            tag=TagResponse.from_orm(tag),
            notes=[NoteResponse.from_orm(note) for note in notes]
        )
    
    def get_notes_by_creation_tag(self, tag_id: UUID) -> List[Note]:
        """Get all notes originally created under a specific tag, in order"""
        return self.db.query(Note)\
            .filter(Note.creation_tag_id == tag_id)\
            .order_by(Note.sequence_number)\
            .all()

# from sqlalchemy.orm import Session
# from fastapi import Depends
# from ..core import get_db
# from ..models import NoteCreate


# class NotesRepo:
#     def __init__(self, db: Session = Depends(get_db)):
#         self.db = db
    
#     async def create(self, order: NoteCreate):
#         # Database operations
#         pass

