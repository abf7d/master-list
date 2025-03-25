
import logging
import string
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
import inspect
from datetime import datetime, timedelta

import requests
from fastapi import HTTPException, Request
import jwt
from jwt import PyJWKClient
from jwt.api_jwk import PyJWK

from .config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("api.auth")


class CachedJWKClient:
    """JWT Key client with caching to minimize network requests."""
    
    def __init__(self, jwks_url: str, cache_ttl: int = 3600):
        """
        Initialize the cached JWK client.
        
        Args:
            jwks_url: URL to the JWKS endpoint
            cache_ttl: Time to live for cached keys in seconds (default: 1 hour)
        """
        self.jwks_url = jwks_url
        self.cache_ttl = cache_ttl
        self.jwk_client = PyJWKClient(jwks_url)
        self.key_cache = {}  # kid -> (key, timestamp)
        self.jwks_cache = None
        self.jwks_cache_time = 0
        
    def get_signing_key_from_jwt(self, token: str, force_refresh: bool = False) -> PyJWK:
        """
        Get the signing key for a JWT token.
        
        Args:
            token: The JWT token
            force_refresh: If True, bypass cache and fetch fresh keys
            
        Returns:
            The signing key
        """
        # Extract the key ID from the token header
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
        except Exception as e:
            logger.error(f"Failed to extract key ID from token: {e}")
            raise
            
        if not kid:
            logger.warning("Token doesn't contain a key ID (kid)")
            raise jwt.InvalidTokenError("Token header missing 'kid' claim")
            
        current_time = time.time()
        
        # Return from cache if available and not expired
        if not force_refresh and kid in self.key_cache:
            key, timestamp = self.key_cache[kid]
            if current_time - timestamp < self.cache_ttl:
                print('keys are cached')
                logger.debug(f"Using cached signing key for kid: {kid}")
                return key
        print('keys not cached')
        # If we're here, we need to fetch the key
        try:
            if force_refresh or (current_time - self.jwks_cache_time > self.cache_ttl):
                logger.info("Fetching fresh JWKS from server")
                self.jwks_cache_time = current_time
                # Use the underlying PyJWKClient to fetch keys
                signing_key = self.jwk_client.get_signing_key_from_jwt(token)
                # Cache the key
                self.key_cache[kid] = (signing_key, current_time)
                print(f'caching keys for {kid}')
                return signing_key
            else:
                # Use existing JWKS cache but look for a different key
                signing_key = self.jwk_client.get_signing_key_from_jwt(token)
                # Cache the key
                self.key_cache[kid] = (signing_key, current_time)
                return signing_key
        except Exception as e:
            logger.error(f"Failed to fetch signing key: {e}")
            raise
            
    def clear_cache(self):
        """Clear the key cache."""
        self.key_cache = {}
        self.jwks_cache_time = 0


def get_token_from_header(request: Request) -> str:
    """Extract the Bearer token from the Authorization header."""
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise HTTPException(status_code=401, detail="Authorization header is expected")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Authorization header must start with Bearer"
        )
    elif len(parts) == 1:
        raise HTTPException(status_code=401, detail="Token not found")
    elif len(parts) > 2:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = parts[1]
    return token


def get_user_email(decoded_payload: Dict[str, Any]) -> str:
    """Extract user email from token payload."""
    emails = decoded_payload.get("emails")
    if not emails or not isinstance(emails, List) or len(emails) == 0:
        raise HTTPException(status_code=401, detail="Email claim not found in token")
    return emails[0]


def normalize_text(text: str) -> str:
    """Replace punctuation with underscore in text."""
    return text.translate(
        str.maketrans(string.punctuation, "_" * len(string.punctuation))
    )


# Create a global instance of the cached client
_jwk_client = None

def get_jwk_client() -> CachedJWKClient:
    """Get or create the global JWK client."""
    global _jwk_client
    if _jwk_client is None:
        jwks_url = settings.JWKS_URL
        _jwk_client = CachedJWKClient(jwks_url)
    return _jwk_client


def verify_token(token: str, audience: str, issuer_url: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Verify a JWT token and return the decoded payload.
    
    Args:
        token: The JWT token
        audience: Expected audience
        issuer_url: Expected issuer
        force_refresh: Whether to force a refresh of the signing keys
        
    Returns:
        The decoded token payload
    """
    jwk_client = get_jwk_client()
    
    try:
        # Get the signing key
        signing_key = jwk_client.get_signing_key_from_jwt(token, force_refresh)
        
        # Decode and validate the token
        decoded_payload = jwt.decode(
            token,
            signing_key.key,
            verify=True,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer_url,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        
        return decoded_payload
        
    except Exception as e:
        # If we fail with cached keys, try once with fresh keys
        if not force_refresh:
            logger.info(f"Token validation failed with cached keys: {e}. Trying with fresh keys.")
            return verify_token(token, audience, issuer_url, True)
        # If we already tried with fresh keys, re-raise the exception
        raise


def authenticate(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Authenticate requests using Azure B2C JWT tokens with key caching.
    
    This decorator validates the token signature and claims, then adds user
    information to the request state.
    """
    async def wrapper(*args: Any, **kwargs: Any) -> Awaitable[Any]:
        request: Request = kwargs["request"]
        logger.debug(f"Authenticating request to {func.__name__}")
        
        # Get JWT token from Authorization header
        token = get_token_from_header(request)
        
        # Get configuration from settings
        tenant_id = settings.TENANT_ID
        audience = settings.AUDIENCE
        issuer_url = f"https://criticalplayground.b2clogin.com/{tenant_id}/v2.0/"
        
        try:
            # Verify the token (with automatic retry using fresh keys if needed)
            decoded_payload = verify_token(token, audience, issuer_url)
            
            # Extract user information
            user_email = get_user_email(decoded_payload)
            user_id = decoded_payload.get("oid")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID claim not found in token")
            
            exp = decoded_payload.get("exp")
            
            # Add user info to request state
            request.state.email = user_email
            request.state.user_id = user_id
            request.state.exp = exp
            request.state.decoded_token = decoded_payload
            
            # Proceed to the endpoint
            return await func(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            logger.warning("Authentication failed: Token expired")
            raise HTTPException(
                status_code=401,
                detail="Token has expired. Please obtain a new token."
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Authentication failed: Invalid token: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid token: {str(e)}"
            )
        except jwt.DecodeError:
            logger.warning("Authentication failed: Unable to decode token")
            raise HTTPException(
                status_code=401, 
                detail="Unable to decode authentication token"
            )
        except jwt.InvalidSignatureError:
            logger.warning("Authentication failed: Invalid signature")
            raise HTTPException(
                status_code=401, 
                detail="Token signature verification failed"
            )
        except jwt.InvalidAudienceError:
            logger.warning("Authentication failed: Invalid audience")
            raise HTTPException(
                status_code=401, 
                detail="Token audience validation failed"
            )
        except jwt.InvalidIssuerError:
            logger.warning("Authentication failed: Invalid issuer")
            raise HTTPException(
                status_code=401, 
                detail="Token issuer validation failed"
            )
        

    # Preserve function signature for FastAPI dependency injection
    wrapper.__signature__ = inspect.Signature(
        parameters=[
            # Skip *args and **kwargs from wrapper parameters
            *filter(
                lambda p: p.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ),
                inspect.signature(wrapper).parameters.values(),
            ),
            # Use all parameters from handler
            *inspect.signature(func).parameters.values(),
        ],
        return_annotation=inspect.signature(func).return_annotation,
    )

    return wrapper


# # Example of using the decorator
# """
# @app.get("/protected-endpoint")
# @authenticate
# async def protected_endpoint(request: Request):
#     # Access user info from request.state
#     user_id = request.state.user_id
#     user_email = request.state.email
    
#     return {"message": f"Hello, {user_email}!"}
# """


# # You can also create a FastAPI dependency for more flexibility
# def get_current_user(request: Request) -> Dict[str, Any]:
#     """
#     FastAPI dependency to get the current authenticated user.
    
#     Example usage:
#         @app.get("/user-info")
#         async def user_info(user: Dict[str, Any] = Depends(get_current_user)):
#             return {"user_id": user["user_id"], "email": user["email"]}
#     """
#     tenant_id = settings.TENANT_ID
#     audience = settings.AUDIENCE
#     issuer_url = f"https://criticalplayground.b2clogin.com/{tenant_id}/v2.0/"
    
#     token = get_token_from_header(request)
#     decoded_payload = verify_token(token, audience, issuer_url)
    
#     user_email = get_user_email(decoded_payload)
#     user_id = decoded_payload.get("oid")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="User ID claim not found in token")
    
#     return {
#         "user_id": user_id,
#         "email": user_email,
#         "decoded_token": decoded_payload
#     }











# import logging
# import string
# from typing import Any, Awaitable, Callable, Dict  # NOQA

# import requests
# from fastapi import HTTPException, Request
# # from jose import jwt
# from .config import settings #DEFAULT_USER,


# import jwt
# from jwt import PyJWKClient


# logging.basicConfig(
#     format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
#     datefmt="%d-%b-%y %H:%M:%S",
# )
# logger = logging.getLogger("plots.auth")


# def get_token_auth_header(request: Request) -> str:
#     """Obtains the Access Token from the Authorization Header."""
#     auth = request.headers.get("Authorization", None)
#     if not auth:
#         raise HTTPException(status_code=401, detail="Authorization header is expected")

#     parts = auth.split()

#     if parts[0].lower() != "bearer" or len(parts) > 2:
#         raise HTTPException(
#             status_code=401, detail="Authorization header must start with Bearer"
#         )
#     elif len(parts) == 1:
#         raise HTTPException(status_code=401, detail="Token not found.")
#     elif len(parts) > 2:
#         raise HTTPException(status_code=401, detail="Invalid Authorization header format")

#     token = parts[1]
#     return token


# def get_user(request: Request) -> Dict[Any, Any]:
#     """Gets user information from Request object."""
#     token = get_token_auth_header(request)
#     return get_user_info(token)


# def normalize_text(text: str) -> str:
#     """Replaces punctuation with underscare in text."""
#     return text.translate(
#         str.maketrans(string.punctuation, "_" * len(string.punctuation))
#     )

# def get_user_info(decoded_payload: Dict[str, Any]) -> Dict[str, Any]:
#     email = decoded_payload.get("emails", None)
#     if email is None:
#         raise HTTPException(status_code=401, detail="Claims not found.")
#     return email[0]


# def authenticate(func: Callable[..., Any]) -> Callable[..., Any]:
#     """Authenticate header information with jwt.

#     This is a decorator for authenticated endpoints in cyto-explorer. In order for
#     authentication to be turned on, the .env file must have the AUTH_BASE_URL,
#     JWKS_ENDPOINT, and ALGORITHM values set.

#     Args:
#         func (Callable): Function to wrap with authentication methods.

#     Returns:
#         Returns a wrapped API endpoint.
#     """
#     import inspect

#     async def wrapper(*args: Any, **kwargs: Any) -> Awaitable[Any]:
#         print('args', kwargs)
#         tenant_id = settings.TENANT_ID
#         audience = settings.AUDIENCE
#         print('tenant_id', tenant_id)
#         print('audience', audience)
#         # return await func(*args, **kwargs)
#         request: Request = kwargs["request"]

#         logging.debug(f"Calling {func.__name__} with auth.")
#         token = get_token_auth_header(request)

#         jwks_url = settings.JWKS_URL
#         issuer_url = f"https://criticalplayground.b2clogin.com/{tenant_id}/v2.0/"
#         jwks_client = PyJWKClient(
#             jwks_url,
#         )
#         signing_key = jwks_client.get_signing_key_from_jwt(token)
#         print(signing_key)
#         try:
#             # Decode without verifying signature to inspect claims
           
#             decoded_payload = jwt.decode(
#                 token,
#                 signing_key.key,
#                 verify=True,
#                 algorithms=["RS256"],
#                 audience=audience,
#                 issuer=issuer_url,
#             )

#         except jwt.ExpiredSignatureError:
#             # Add logging
#             print('ExpiredSignatureError')
#             raise HTTPException(
#                 status_code=401,
#                 detail="Expired signature. Please obtain a new token.",
#             )
#         except jwt.DecodeError as ex:
#             # Add logging
#             print('DecodeError')
#             raise HTTPException(
#                 status_code=401, detail="Unable to decode authentication token."
#             )
#         except Exception as ex:
#             # Add logging
#             print('General Exception', ex)
#             raise HTTPException(
#                 status_code=401, detail="Unable to parse authentication token."
#             )
        
#         # print('decoded_payload', decoded_payload)
#         user_email = get_user_info(decoded_payload)


#         user_id = decoded_payload.get("oid", None)
#         exp =  exp_claim = decoded_payload.get("exp", None)

#         # Check if user id exists in User DB, if not create the entry


#         # print('user_id', user_id)
#         # user_data = "tempuser"
#         request.state.email = user_email
#         request.state.user_id = user_id #normalize_text(email)
#         request.state.exp = exp
#         request.state.decoded_token = decoded_payload
#         return await func(*args, **kwargs)

#     wrapper.__signature__ = inspect.Signature(  # type: ignore
#         parameters=[
#             # Skip *args and **kwargs from wrapper parameters:
#             *filter(
#                 lambda p: p.kind
#                 not in (
#                     inspect.Parameter.VAR_POSITIONAL,
#                     inspect.Parameter.VAR_KEYWORD,
#                 ),
#                 inspect.signature(wrapper).parameters.values(),
#             ),
#             # Use all parameters from handler
#             *inspect.signature(func).parameters.values(),
#         ],
#         return_annotation=inspect.signature(func).return_annotation,
#     )

#     return wrapper
