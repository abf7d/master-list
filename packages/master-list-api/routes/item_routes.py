from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from fastapi import APIRouter, Depends
from services.note_service import NoteService
from core.database import get_db
from models.models import CreateNoteGroup, MoveNoteGroup, NoteItemsResponse, ResponseData
from core.auth import authenticate

from sqlalchemy.orm import Session
import logging
from services.graph_service import GraphService
from services.token_service import TokenService

router = APIRouter()
# router = APIRouter(prefix="/account")

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")


# Dependency to get NoteService
def get_note_service(db: Session = Depends(get_db)):
    return NoteService(db)

def get_graph_service():
    return GraphService()


def get_token_service():
    return TokenService()

# For saving note items on a note page
#Items
@router.post("/note-items/", response_model=NoteItemsResponse)
@authenticate
async def post_note_items(request: Request, note_group: CreateNoteGroup, 
        note_service: NoteService = Depends(get_note_service),):
    print('NOTE GROUP', note_group)
    
    note_service.update_note_items(note_group, request.state.user_id)
   
    # Convert db_note to NoteResponse format
    return NoteItemsResponse(
        message="Success",
        error=None,
        data='test1234'
    )

  

# Items
@router.post("/note-items/move", response_model=ResponseData)
@authenticate
async def move_note_items(request: Request, note_group: MoveNoteGroup, 
        note_service: NoteService = Depends(get_note_service),):
    print('MOVE GROUP', note_group)
    
    response = note_service.move_note_items(note_group, request.state.user_id)
   
    # Convert db_note to NoteResponse format
    return response

