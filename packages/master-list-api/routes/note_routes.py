
from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Request

from fastapi import APIRouter, Depends
from services.note_service import NoteService
from core.database import get_db
from models.models import ResponseData
from core.auth import authenticate

from sqlalchemy.orm import Session
import logging
from services.graph_service import GraphService
from services.token_service import TokenService

router = APIRouter()

# router = APIRouter(prefix="/notes", tags=["notes"])

# @router.get("/", …)  

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

@router.delete("/note/{note_id}", response_model=ResponseData,)
@authenticate
async def delete_tag_button(request: Request, note_id: UUID,
    graph_service: GraphService = Depends(get_graph_service),
    note_service: NoteService = Depends(get_note_service),
    token_service: TokenService = Depends(get_token_service)):
    # tag_buttons_db.append(tag_button)
    # Convert it to a TagCreation by unpacking and adding the id
    
    # Integrate Redis!!!
    # claims = await graph_service.get_claims(request.state.user_id)
    # role = token_service.get_role(request.state.user_id, request.state.exp, claims, request.state.decoded_token)

    # if(role == "user" or role == "admin"):
    print('IS AUTHORIZED!!!!!!!!!')
    
    success = note_service.delete_note(note_id, request.state.user_id)
    print('Finished Save!!!!!!!!!')
    # Now create the TagResponse
    response = ResponseData(
        message="Note deleted successfully",
        error="",
        data=success
    )
    # data = TagCreation(tag_button.name, tag_button.color, tag_button.backgroundcolor, '1234')
    # response = TagResponse('success', None, data)
    print('tag response', response)
    return response



@router.get("/notes/", response_model=ResponseData)
@authenticate
async def get_tags(
    request: Request,
    query: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, alias="pageSize", ge=1, le=100, description="Number of tags per page"),
    id: Optional[str] = None,
    graph_service: GraphService = Depends(get_graph_service),
    note_service: NoteService = Depends(get_note_service),
):
    """Get a list of Notes"""
   
    # data = note_service.get_tags(request.state.user_id, query, page, pageSize, parent_tag_id=None, )
    data = note_service.get_notes(request.state.user_id, query, page, pageSize, id=id, parent_tag_id=None )
    response = ResponseData(message='Success', error=None, data=data )
    print('data', data)
    return response


@router.post("/note", response_model=ResponseData,)
@authenticate
async def create_note(request: Request,
    graph_service: GraphService = Depends(get_graph_service),
    note_service: NoteService = Depends(get_note_service),
    token_service: TokenService = Depends(get_token_service)):
   
    note_info = note_service.create_note(request.state.user_id)
    response = ResponseData(
        message="Note created successfully",
        error="",
        data=note_info
    )
    # data = TagCreation(tag_button.name, tag_button.color, tag_button.backgroundcolor, '1234')
    return response


# GET /notes/{note_id}/pages/{idx} 
