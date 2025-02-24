from typing import Any, List
from datetime import datetime, timedelta
import uuid
import jwt
from dataclasses import dataclass
from typing import Optional

@dataclass
class JwtResponse:
    token: str
    expires_at: int

@dataclass
class JwtSettings:
    issuer: str
    audience: str

class TokenService:
    def __init__(self, settings: JwtSettings):
        self._settings = settings

# identity: dict,
    def get_token(self, username: str, exp: Any, groups: List[dict]) -> Optional[JwtResponse]:
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
            
            # Create basic claims
            guid = str(uuid.uuid4())
            iat = int(now.timestamp())
            
            # Get expiration from identity
            exp_claim = exp #identity.get(EXP)
            if exp_claim is None:
                raise ValueError(f"Missing required claim: {ROL}")

            # Create claims list
            claims = {
                "sub": username,
                "jti": guid,
                "iat": iat,
                "exp": int(exp_claim),
                # "iss": self._settings.issuer,
                # "aud": self._settings.audience,
                "nbf": int(now.timestamp()),
            }

            # Add group claims
            for group in groups:
                claims.update(group)

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
                ExpiresAt=int(exp_claim)
            )

        except Exception as ex:
            print(f"Error creating token: {str(ex)}", file=sys.stderr)
            return None