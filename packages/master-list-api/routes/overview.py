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







# Overview is a "sub resource" that encapsulates a bunch of repeated endpoints for the tags and notes and helps us keep DRY
# Keep overview as the sub-resource name—/notes/{id}/overview, /tags/{id}/overview.
# Implement all overview-related endpoints once in routers/overview.py using a dynamic prefix (/{parent}/{parent_id}/overview).
# Let OverviewService do the branching on parent, so business logic remains DRY.



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


# overview Gets All Elements for the Page
# For loading elemetns on a note page, perhaps call this get_note_profile or get_list_page 
@router.get("/note-items/{parent_tag_id}/{list_type}", response_model=NoteItemsResponse)
@authenticate
async def get_note_items(request: Request, parent_tag_id: str, list_type: str,  
                         page: Optional[int] = Query(
                            None,  # default value if caller omits it
                            ge=1,
                            description="Page number (1-based); omit for first page"
    ), note_service: NoteService = Depends(get_note_service),): 
    return note_service.get_note_items(parent_tag_id, request.state.user_id, list_type, page)


# overview Deletes a Paginatated Page from the resource
@router.delete("/page/{parent_tag_id}/{list_type}", response_model=NoteItemsResponse)
@authenticate
async def delete_page(request: Request, parent_tag_id: str, list_type: str,  
                         page: Optional[int] = Query(
                            None,  # default value if caller omits it
                            ge=1,
                            description="Page number (1-based); omit for first page"
    ), note_service: NoteService = Depends(get_note_service),): 
    note_service.delete_page(parent_tag_id, request.state.user_id, list_type, page)
    response = ResponseData(
        message="Note created successfully",
        error="",
        data={"success": True}  
    )
    return response