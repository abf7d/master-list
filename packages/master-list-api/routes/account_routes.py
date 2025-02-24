from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from db_init.schemas import TagResponse, NoteGroupResponse
from core.auth import authenticate
from services.token_service import TokenService

from sqlalchemy.orm import Session
from typing import List
from fastapi import Request
from services.graph_service import GraphService
from core.account_mapper import AccountMapper
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

def get_token_service():
    return TokenService()

def get_account_mapper():
    return AccountMapper()


@router.get("/get-token/", response_model=List[TagResponse])
@authenticate
async def get_tags(
    request: Request,
    account_mapper: AccountMapper = Depends(get_account_mapper),
    token_service: TokenService = Depends(get_token_service),
    note_service: NoteService = Depends(get_note_service),
    graph_service: GraphService = Depends(get_graph_service)
):
    """Create a new tag"""
    print('USERID!!!!!!!!! ', request.state.user_id)
    # this should work
    claims = await graph_service.get_claims(request.state.user_id)
    print('CLAIMS!!!!!!!!! ', claims)
    
    # need to test this and user_identity might not be the correct format and I might need to change the code
    account = account_mapper.map_claims_to_account(claims, request.state.user_identity) #(request.state.user_id)
    print('ACCOUNT!!!!!!!!! ', account)

    #need to test this
    token = token_service.get_token(request.state.user_id, request.state.exp, claims)
    result = {
        "Result": token,
    }
    print('RESULT!!!!!!!!! ', result)


    note_service.get_tags(parent_tag_id=None)
    return result


