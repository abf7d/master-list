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
    prefix="/{list_type}/{list_id}/page",
    tags=["pages"],
)

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")

# class ListType(str, Enum):
#     notes = "note"
#     tags = "tag"

# Dependency to get NoteService
def get_overview_service(db: Session = Depends(get_db)):
    return OverviewService(db)

def get_graph_service():
    return GraphService()

def get_token_service():
    return TokenService()


# overview Deletes a Paginatated Page from the resource
@router.delete("/", response_model=NoteItemsResponse)
@authenticate
async def delete_page(request: Request, list_type: ListType, list_id: str,  
                         page: Optional[int] = Query(
                            None,  # default value if caller omits it
                            ge=1,
                            description="Page number (1-based); omit for first page"
    ), overview_service: OverviewService = Depends(get_overview_service),): 
    overview_service.delete_page(list_id, request.state.user_id, list_type, page)
    response = ResponseData(
        message="Note created successfully",
        error="",
        data={"success": True}  
    )
    return response


# update api ts service and fix route path

# from enum import Enum
# from uuid import UUID

# from fastapi import APIRouter, Depends, Path, HTTPException

# class Parent(str, Enum):
#     notes = "notes"
#     tags = "tags"


# router = APIRouter(
#     prefix="/{parent}/{parent_id}/pages",
#     tags=["pages"],
# )

# @router.post("/", response_model=PageOut, status_code=201)
# async def create_page(
#     parent: Parent,             # notes | tags  (Enum as in previous example)
#     parent_id: UUID,
#     body: PageCreate,           # e.g. {"title": "New Page"}
#     svc: PageService = Depends(),
#     user = Depends(current_user),
# ):
#     return await svc.create(parent, parent_id, body, user)

# @router.get("/{page_no}", ...)      # fetch a page
# @router.delete("/{page_no}", ...)   # delete a page