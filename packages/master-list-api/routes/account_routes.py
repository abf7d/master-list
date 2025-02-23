from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from db_init.schemas import TagResponse, NoteGroupResponse
from core.auth import authenticate

from sqlalchemy.orm import Session
from typing import List
from fastapi import Request
from services.graph_service import GraphService
import logging

router = APIRouter(prefix="/account")

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")

# Dependency to get NoteService
def get_note_service(db: Session = Depends(get_db)):
    return NoteService(db)

def get_graph_service():
    return GraphService()

@router.get("/get-token/", response_model=List[TagResponse])
@authenticate
async def get_tags(
    request: Request,
    note_service: NoteService = Depends(get_note_service),
    graph_service: GraphService = Depends(get_graph_service)
):
    """Create a new tag"""
    print('USERID!!!!!!!!! ', request.state.user_id)
    claims = await graph_service.get_claims(request.state.user_id)
    print('CLAIMS!!!!!!!!! ', claims)

    return note_service.get_tags(parent_tag_id=None)


