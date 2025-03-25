from typing import Any, List
from datetime import datetime, timedelta
import uuid
import jwt
from dataclasses import dataclass
from typing import Optional
from core.config import settings
from services.graph_service import Claim
import logging
from pydantic import BaseModel

""" Initialize the logger """
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("routers.bins")

@dataclass
class JwtResponse:
    Token: str
    ExpiresAt: int
class TokenService:

# identity: dict,
    def get_token(self, username: str, exp: Any, groups: List[Claim], decoded_token: dict) -> JwtResponse:
        """
        Create an unsigned JWT token with claims.
        
        Args:
            username: The username to include in the token
            identity: Dictionary containing identity claims
            groups: List of group claims
            
        Returns:
            JwtResponse containing the token and expiration time, or None if creation fails
        """
        try:
            # Constants
            ROL = "rol"
            ID = "id"
            # EXP = "exp"

            # Get current time
            now = datetime.utcnow()

            isAdmin = False
            isAuthorized = False
            for group in groups:
                if group.value == 'Site Admin':
                    isAdmin = True
                if group.value == 'Authorized User':
                    isAuthorized = True

            # Get role
            role = 'guest'
            if isAdmin:
                role = 'admin'
            elif isAuthorized:
                role = 'user'
            
            # Create basic claims
            guid = str(uuid.uuid4())
            iat = int(now.timestamp())
            iss = decoded_token.get("iss", None)
            aud = decoded_token.get("aud", None)
            exp = decoded_token.get("exp", None)

            # Get expiration from identity
            # exp_claim = exp #identity.get(EXP)
            if exp is None:
                raise ValueError(f"Missing required claim: exp")

            # Create claims list
            claims = {
                "sub": username,
                "jti": guid,
                "iat": iat,
                "exp": int(exp),
                "iss": iss,
                "aud": aud,
                "nbf": int(now.timestamp()),
                "rol": role,
                "group": [group.value for group in groups],
            }


            # Create header with "none" algorithm
            headers = {
                "alg": "none",
                "typ": "JWT"
            }

            # Create the unsigned token
            token = jwt.encode(
                payload=claims,
                key="",  # Empty key for unsigned token
                algorithm="none",
                headers=headers
            )

            return JwtResponse(
                Token=token,
                ExpiresAt=int(exp)
            )

        except Exception as ex:
            logger.exception(f"Error creating token: {str(ex)}")
            return None
    
    # TODO: change to dictionary for gtroups so you return mutliple    
    def get_role(self, username: str, exp: Any, groups: List[Claim], decoded_token: dict) -> JwtResponse:
        """
        Create an unsigned JWT token with claims.
        
        Args:
            username: The username to include in the token
            identity: Dictionary containing identity claims
            groups: List of group claims
            
        Returns:
            JwtResponse containing the token and expiration time, or None if creation fails
        """
        isAuthorized = False
        for group in groups:
            if group.value == 'Site Admin':
                isAdmin = True
            if group.value == 'Authorized User':
                isAuthorized = True
        
            # Get role
        role = 'guest'
        if isAdmin:
            role = 'admin'
        elif isAuthorized:
            role = 'user'

        return role