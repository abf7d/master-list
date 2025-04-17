from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import Request

from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from models.models import CreateNoteGroup, NoteItemsResponse, ResponseData, TagButton, TagCreation, TagResponse, NoteGroupResponse
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


@router.get("/tags/", response_model=ResponseData)
@authenticate
async def get_tags(
    request: Request,
    query: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, alias="pageSize", ge=1, le=100, description="Number of tags per page"),
    graph_service: GraphService = Depends(get_graph_service),
    note_service: NoteService = Depends(get_note_service),
):
    """Create a new tag"""
    # print('USERID!!!!!!!!! ', request.state.user_id)
    # claims = await graph_service.get_claims(request.state.user_id)
    # print('CLAIMS!!!!!!!!! ', request.state.user_id, query, page, pageSize)
    data = note_service.get_tags(request.state.user_id, query, page, pageSize, parent_tag_id=None, )
    response = ResponseData(message='Success', error=None, data=data )
    print('data', data)
    return response
# @router.get("/tags/{parent_tag_id}/children", response_model=List[TagResponse])
# async def get_child_tags(
#     parent_tag_id: UUID,
#     note_service: NoteService = Depends(get_note_service)
# ):
#     """Get child tags for a specific parent tag"""
#     return note_service.get_tags(parent_tag_id=parent_tag_id)



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



# @router.get("/note-items/{note_id}", response_model=NoteResponse)
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


@router.post("/note-items/", response_model=NoteItemsResponse)
@authenticate
async def post_note_items(request: Request, note_group: CreateNoteGroup, 
        note_service: NoteService = Depends(get_note_service),):
    print('NOTE GROUP', note_group)
    
    note_service.update_note_items(note_group, request.state.user_id)
    
    
    # db_note = Note(
    #     title=note.title,
    #     content=note.content,
    #     tags=",".join(note.tags) if note.tags else ""
    # )
    # db.add(db_note)
    # db.commit()
    # db.refresh(db_note)
    
    # Convert db_note to NoteResponse format
    return NoteItemsResponse(
        message="Success",
        error=None,
        data='test1234'
    )


@router.get("/note-items/{parent_tag_id}/{list_type}", response_model=NoteItemsResponse)
@authenticate
async def get_note_items(request: Request, parent_tag_id: str, list_type: str,
        note_service: NoteService = Depends(get_note_service),):
    return note_service.get_note_items(parent_tag_id, request.state.user_id, list_type)
    
    
    # db_note = Note(
    #     title=note.title,
    #     content=note.content,
    #     tags=",".join(note.tags) if note.tags else ""
    # )
    # db.add(db_note)
    # db.commit()
    # db.refresh(db_note)
    
    # Convert db_note to NoteResponse format
    return NoteItemsResponse(
        message="Success",
        error=None,
        data='test1234'
    )














# @router.post("/tags/{tag_id}/notes/", response_model=NoteGroupResponse)
# async def create_notes_for_tag(
#     tag_id: UUID, 
#     content_list: List[str],
#     note_service: NoteService = Depends(get_note_service)
# ):
#     """Create notes under an existing tag"""
#     try:
#         return note_service.create_notes_for_tag(tag_id=tag_id, content_list=content_list)
#     except NoResultFound as e:
#         raise HTTPException(status_code=404, detail=str(e))

# @router.get("/tags/{tag_id}/notes/", response_model=NoteGroupResponse)
# async def get_note_group(
#     tag_id: UUID,
#     note_service: NoteService = Depends(get_note_service)
# ):
#     """Get all notes for a specific tag"""
#     note_group = note_service.get_note_group_by_tag_id(tag_id)
#     if not note_group:
#         raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
#     return note_group

# @router.patch("/tags/{tag_id}/name", response_model=TagResponse)
# async def update_tag_name(
#     tag_id: UUID,
#     new_name: str,
#     note_service: NoteService = Depends(get_note_service)
# ):
#     """Update a tag's name"""
#     try:
#         return note_service.update_tag_name(tag_id=tag_id, new_name=new_name)
#     except NoResultFound as e:
#         raise HTTPException(status_code=404, detail=str(e))

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