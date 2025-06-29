from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import Request

from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from models.models import CreateNoteGroup, MoveNoteGroup, NoteItemsResponse, ResponseData, TagButton, TagCreation, TagResponse, NoteGroupResponse
from core.auth import authenticate

from sqlalchemy.orm import Session
from typing import List
import logging
from services.graph_service import GraphService
from services.token_service import JwtResponse, TokenService

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

#TODO: move this to tag_routes
@router.delete("/tag/{tag_name}", response_model=ResponseData,)
@authenticate
async def delete_tag_button(request: Request, tag_name: str,
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
    
    success = note_service.delete_tag(tag_name, request.state.user_id)
    print('Finished Save!!!!!!!!!')
    # Now create the TagResponse
    response = ResponseData(
        message="Tag deleted successfully",
        error="",
        data=success
    )
    # data = TagCreation(tag_button.name, tag_button.color, tag_button.backgroundcolor, '1234')
    # response = TagResponse('success', None, data)
    print('tag response', response)
    return response


#TODO: move this to tag_routes
@router.post("/tag", response_model=ResponseData,)
@authenticate
async def create_tag_button(request: Request, tag_button: TagButton,
    graph_service: GraphService = Depends(get_graph_service),
    note_service: NoteService = Depends(get_note_service),
    token_service: TokenService = Depends(get_token_service)):
    # tag_buttons_db.append(tag_button)
    # Convert it to a TagCreation by unpacking and adding the id
    
    # Integrate Redis!!!
    # claims = await graph_service.get_claims(request.state.user_id)
    # role = token_service.get_role(request.state.user_id, request.state.exp, claims, request.state.decoded_token)

    # tag_creation = TagCreation(**tag_button.dict(), id=-1)

    # if(role == "user" or role == "admin"):
    print('IS AUTHORIZED!!!!!!!!!')
    # index = note_service.create_tag(tag_button.name, request.state.user_id, tag_button.color, tag_button.backgroundcolor)
    tag_info = note_service.create_tag(tag_button.name, request.state.user_id)
    print('Finished Save!!!!!!!!!')
    # tag_creation.id = tag_info
    # Now create the TagResponse
    response = ResponseData(
        message="Tag created successfully",
        error="",
        data=tag_info
    )
    # data = TagCreation(tag_button.name, tag_button.color, tag_button.backgroundcolor, '1234')
    # response = TagResponse('success', None, data)
    print('tag response', response)
    return response

@router.get("/tags/", response_model=ResponseData)
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
    """Create a new tag"""
    # print('USERID!!!!!!!!! ', request.state.user_id)
    # claims = await graph_service.get_claims(request.state.user_id)
    # print('CLAIMS!!!!!!!!! ', request.state.user_id, query, page, pageSize)
    data = note_service.get_tags(request.state.user_id, query, page, pageSize, id, parent_tag_id=None, )
    response = ResponseData(message='Success', error=None, data=data )
    print('data', data)
    return response













#  GET /tags/{tag_id}/pages/{idx}