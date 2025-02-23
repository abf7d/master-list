from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from db_init.schemas import TagResponse, NoteGroupResponse
from core.auth import authenticate

from sqlalchemy.orm import Session
from typing import List
import logging

router = APIRouter(prefix="/account")

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")

# Dependency to get NoteService
def get_note_service(db: Session = Depends(get_db)):
    return NoteService(db)

@router.get("/get-token/", response_model=List[TagResponse])
@authenticate
async def get_tags(
    note_service: NoteService = Depends(get_note_service)
):
    """Create a new tag"""
    return note_service.get_tags(parent_tag_id=None)