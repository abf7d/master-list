from fastapi import APIRouter, Depends, HTTPException
from services.note_service import NoteService
from core.database import get_db
from models.models import TagResponse, NoteGroupResponse
from core.auth import authenticate
from services.token_service import JwtResponse, TokenService

from sqlalchemy.orm import Session
from typing import List
from fastapi import Request
from services.graph_service import GraphService
from core.account_mapper import AccountMapper
import logging
from pydantic import BaseModel

from repos.user_repo import UserRepo
from services.account_service import AccountService


router = APIRouter(prefix="/account")

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepo(db)

def get_user_service(repo: UserRepo = Depends(get_user_repository)):
    return AccountService(repo)

# Dependency to get NoteService
def get_note_service(db: Session = Depends(get_db)):
    return NoteService(db)

def get_graph_service():
    return GraphService()

def get_token_service():
    return TokenService()

def get_account_mapper():
    return AccountMapper()

class TokenResponse(BaseModel):
    Result: JwtResponse

@router.get("/get-token/", response_model=TokenResponse)
@authenticate
async def get_token(
    request: Request,
    account_mapper: AccountMapper = Depends(get_account_mapper),
    token_service: TokenService = Depends(get_token_service),
    note_service: NoteService = Depends(get_note_service),
    account_service: AccountService = Depends(get_user_service),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Get token for the authenticated user and ensure they exist in the database.
    
    This endpoint:
    1. Validates the token (via @authenticate decorator)
    2. Fetches additional claims from the graph service
    3. Creates or updates the user in the database
    4. Generates and returns a token for the user
    """
    print('USERID!!!!!!!!! ', request.state.user_id)
    # this should work
    claims = await graph_service.get_claims(request.state.user_id)
    print('CLAIMS!!!!!!!!! ', claims)
    
    # need to test this and user_identity might not be the correct format and I might need to change the code
    account = account_mapper.map_claims_to_account(claims, request.state.decoded_token) #(request.state.user_id)
    print('ACCOUNT!!!!!!!!! ', account)

    user = account_service.get_or_create_user_from_token(
        oauth_id=request.state.user_id,
        decoded_token=request.state.decoded_token
    )
    
    #need to test this
    token = token_service.get_token(request.state.user_id, request.state.exp, claims, request.state.decoded_token)
    
    # Check if user exists in database
    # user = db.query(User).filter(User.oauth_id == oauth_id).first()
    
    result: TokenResponse = TokenResponse(Result=token)
    
    print('RESULT!!!!!!!!! ', result)

    # note_service.get_tags(parent_tag_id=None)
    return result


