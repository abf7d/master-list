from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound


from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from db_init.schemas import TagResponse, NoteGroupResponse

from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

# Dependency to get NoteService
def get_note_service(db: Session = Depends(get_db)):
    return NoteService(db)

# @router.get("/tags/", response_model=TagResponse)
# async def get_tags(
#     name: str, 
#     parent_tag_id: Optional[UUID] = None,
#     note_service: NoteService = Depends(get_note_service)
# ):
#     """Create a new tag"""
#     return note_service.create_tag(name=name, parent_tag_id=parent_tag_id)
@router.post("/tags/", response_model=TagResponse)
async def create_tag(
    name: str, 
    parent_tag_id: Optional[UUID] = None,
    note_service: NoteService = Depends(get_note_service)
):
    """Create a new tag"""
    return note_service.create_tag(name=name, parent_tag_id=parent_tag_id)

@router.post("/tags/{tag_id}/notes/", response_model=NoteGroupResponse)
async def create_notes_for_tag(
    tag_id: UUID, 
    content_list: List[str],
    note_service: NoteService = Depends(get_note_service)
):
    """Create notes under an existing tag"""
    try:
        return note_service.create_notes_for_tag(tag_id=tag_id, content_list=content_list)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/tags/{tag_id}/notes/", response_model=NoteGroupResponse)
async def get_note_group(
    tag_id: UUID,
    note_service: NoteService = Depends(get_note_service)
):
    """Get all notes for a specific tag"""
    note_group = note_service.get_note_group_by_tag_id(tag_id)
    if not note_group:
        raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
    return note_group

@router.patch("/tags/{tag_id}/name", response_model=TagResponse)
async def update_tag_name(
    tag_id: UUID,
    new_name: str,
    note_service: NoteService = Depends(get_note_service)
):
    """Update a tag's name"""
    try:
        return note_service.update_tag_name(tag_id=tag_id, new_name=new_name)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# from fastapi import APIRouter, Depends, HTTPException
# from services.note_service import NoteService
# from db_init.schemas import ( CreateNoteGroup, NoteResponse )
# from core.database import get_db
# from models.models import Note

# from sqlalchemy.orm import Session
# from typing import List
# import uuid

# router = APIRouter()

# # @router.post("/notes")
# # async def create_order(order: NoteCreate, service: NoteService = Depends()):
# #     return await service.create_order(order)

# def get_note_service(db: Session = Depends(get_db)):
#     return NoteService(db)


# @router.post("/notes/", response_model=NoteResponse)
# async def create_note(note: CreateNoteGroup, db: Session = Depends(get_db)):
#     db_note = Note(
#         title=note.title,
#         content=note.content,
#         tags=",".join(note.tags) if note.tags else ""
#     )
#     db.add(db_note)
#     db.commit()
#     db.refresh(db_note)
    
#     # Convert db_note to NoteResponse format
#     return NoteResponse(
#         id=db_note.id,
#         title=db_note.title,
#         content=db_note.content,
#         tags=db_note.tags.split(",") if db_note.tags else [],
#         created_at=db_note.created_at,
#         updated_at=db_note.updated_at
#     )

# @router.get("/notes/", response_model=List[NoteResponse])
# async def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     notes = db.query(Note).offset(skip).limit(limit).all()
#     return [
#         NoteResponse(
#             id=note.id,
#             title=note.title,
#             content=note.content,
#             tags=note.tags.split(",") if note.tags else [],
#             created_at=note.created_at,
#             updated_at=note.updated_at
#         ) for note in notes
#     ]

# @router.get("/notes/{note_id}", response_model=NoteResponse)
# async def get_note(note_id: str, db: Session = Depends(get_db)):
#     try:
#         note_uuid = uuid.UUID(note_id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid UUID format")
        
#     note = db.query(Note).filter(Note.id == note_uuid).first()
#     if note is None:
#         raise HTTPException(status_code=404, detail="Note not found")
        
#     return NoteResponse(
#         id=note.id,
#         title=note.title,
#         content=note.content,
#         tags=note.tags.split(",") if note.tags else [],
#         created_at=note.created_at,
#         updated_at=note.updated_at
#     )

# # @router.put("/notes/{note_id}", response_model=NoteResponse)
# # async def update_note(note_id: str, note_update: NoteCreate, db: Session = Depends(get_db)):
# #     try:
# #         note_uuid = uuid.UUID(note_id)
# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Invalid UUID format")
        
# #     db_note = db.query(NoteDB).filter(NoteDB.id == note_uuid).first()
# #     if db_note is None:
# #         raise HTTPException(status_code=404, detail="Note not found")
        
# #     db_note.title = note_update.title
# #     db_note.content = note_update.content
# #     db_note.tags = ",".join(note_update.tags) if note_update.tags else ""
    
# #     db.commit()
# #     db.refresh(db_note)
    
# #     return NoteResponse(
# #         id=db_note.id,
# #         title=db_note.title,
# #         content=db_note.content,
# #         tags=db_note.tags.split(",") if db_note.tags else [],
# #         created_at=db_note.created_at,
# #         updated_at=db_note.updated_at
# #      )

# @router.delete("/notes/{note_id}")
# async def delete_note(note_id: str, db: Session = Depends(get_db)):
#     try:
#         note_uuid = uuid.UUID(note_id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid UUID format")
        
#     db_note = db.query(Note).filter(Note.id == note_uuid).first()
#     if db_note is None:
#         raise HTTPException(status_code=404, detail="Note not found")
        
#     db.delete(db_note)
#     db.commit()
    
#     return {"message": "Note deleted successfully"}