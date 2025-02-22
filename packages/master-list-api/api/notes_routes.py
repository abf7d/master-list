from fastapi import APIRouter, Depends, HTTPException
from ..services.notes_service import NotesService
from ..models import ( NoteCreate, NoteResponse, NoteDB )

from sqlalchemy.orm import Session
from typing import List
import uuid

router = APIRouter()

@router.post("/notes")
async def create_order(order: NoteCreate, service: NotesService = Depends()):
    return await service.create_order(order)


@router.post("/notes/", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    db_note = NoteDB(
        title=note.title,
        content=note.content,
        tags=",".join(note.tags) if note.tags else ""
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Convert db_note to NoteResponse format
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        tags=db_note.tags.split(",") if db_note.tags else [],
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

@router.get("/notes/", response_model=List[NoteResponse])
async def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = db.query(NoteDB).offset(skip).limit(limit).all()
    return [
        NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            tags=note.tags.split(",") if note.tags else [],
            created_at=note.created_at,
            updated_at=note.updated_at
        ) for note in notes
    ]

@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, db: Session = Depends(get_db)):
    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    note = db.query(NoteDB).filter(NoteDB.id == note_uuid).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
        
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        tags=note.tags.split(",") if note.tags else [],
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteCreate, db: Session = Depends(get_db)):
    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    db_note = db.query(NoteDB).filter(NoteDB.id == note_uuid).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
        
    db_note.title = note_update.title
    db_note.content = note_update.content
    db_note.tags = ",".join(note_update.tags) if note_update.tags else ""
    
    db.commit()
    db.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        tags=db_note.tags.split(",") if db_note.tags else [],
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

@router.delete("/notes/{note_id}")
async def delete_note(note_id: str, db: Session = Depends(get_db)):
    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    db_note = db.query(NoteDB).filter(NoteDB.id == note_uuid).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
        
    db.delete(db_note)
    db.commit()
    
    return {"message": "Note deleted successfully"}