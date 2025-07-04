from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from fastapi import APIRouter, Depends
from services.overview_service import OverviewService
from core.database import get_db
from models.models import CreateNoteGroup, ListType, MoveNoteGroup, NoteItemsResponse, ResponseData
from core.auth import authenticate

from sqlalchemy.orm import Session
import logging
from services.graph_service import GraphService
from services.token_service import TokenService

router = APIRouter(
    prefix="/{list_type}/{list_id}/overview",
    tags=["overview"],
)

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")

# Dependency to get NoteService
def get_overview_service(db: Session = Depends(get_db)):
    return OverviewService(db)

def get_graph_service():
    return GraphService()


def get_token_service():
    return TokenService()

# overview Gets All Elements for the Page
# For loading elemetns on a note page, perhaps call this get_note_profile or get_list_page 
@router.get("/", response_model=NoteItemsResponse)
@authenticate
async def get_note_items(request: Request, list_type: ListType, list_id: str,  
                         page: Optional[int] = Query(
                            None,  # default value if caller omits it
                            ge=1,
                            description="Page number (1-based); omit for first page"
    ), overview_service: OverviewService = Depends(get_overview_service),): 
    return overview_service.get_note_items(list_id, request.state.user_id, list_type, page)

