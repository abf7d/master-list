import logging
import string
from typing import Any, Awaitable, Callable, Dict  # NOQA

import requests
from fastapi import HTTPException, Request
# from jose import jwt
from .config import settings #DEFAULT_USER,


import jwt
from jwt import PyJWKClient


# def token_is_valid(tenant_id, audience, token):
#     jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
#     issuer_url = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
#     jwks_client = PyJWKClient(
#         jwks_url,
#     )
#     signing_key = jwks_client.get_signing_key_from_jwt(token)
#     return jwt.decode(
#         token,
#         signing_key.key,
#         verify=True,
#         algorithms=["RS256"],
#         audience=audience,
#         issuer=issuer_url,
#     )


logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("plots.auth")

# IS_OFFLINE = (
#     SETTINGS.AUTH_BASE_URL is None
#     and SETTINGS.JWKS_ENDPOINT is None
#     and SETTINGS.ALGORITHMS is None
# )
# if IS_OFFLINE:
#     logger.warning(
#         "AUTH_BASE_URL, JWKS_ENDPOINT, and/or ALGORITHMS is not defined in the "
#         + "the environment file. Endpoints will not be authenticated."
#     )


# def get_user_info(token: str) -> Dict[str, Any]:
#     """Obtains the data for a user from the 'me' endpoint given a Bearer token.

#     Args:
#         token: Bearer token from Authorization Header
#     """
#     auth_url = settings.auth_url
#     headers = {"Authorization": "Bearer " + token}
#     body_data = {"json": True}
#     userData = requests.post(
#         auth_url,
#         data=body_data,
#         headers=headers,
#     ).json()
#     return userData


def get_token_auth_header(request: Request) -> str:
    """Obtains the Access Token from the Authorization Header."""
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise HTTPException(status_code=401, detail="Authorization header is expected")

    parts = auth.split()

    if parts[0].lower() != "bearer" or len(parts) > 2:
        raise HTTPException(
            status_code=401, detail="Authorization header must start with Bearer"
        )
    elif len(parts) == 1:
        raise HTTPException(status_code=401, detail="Token not found.")

    token = parts[1]
    return token


def get_user(request: Request) -> Dict[Any, Any]:
    """Gets user information from Request object."""
    token = get_token_auth_header(request)
    return get_user_info(token)


def normalize_text(text: str) -> str:
    """Replaces punctuation with underscare in text."""
    return text.translate(
        str.maketrans(string.punctuation, "_" * len(string.punctuation))
    )

def get_user_info(decoded_payload: Dict[str, Any]) -> Dict[str, Any]:
    email = decoded_payload.get("emails", None)
    if email is None:
        raise HTTPException(status_code=401, detail="Claims not found.")
    return email[0]


def authenticate(func: Callable[..., Any]) -> Callable[..., Any]:
    """Authenticate header information with jwt.

    This is a decorator for authenticated endpoints in cyto-explorer. In order for
    authentication to be turned on, the .env file must have the AUTH_BASE_URL,
    JWKS_ENDPOINT, and ALGORITHM values set.

    Args:
        func (Callable): Function to wrap with authentication methods.

    Returns:
        Returns a wrapped API endpoint.
    """
    import inspect

    async def wrapper(*args: Any, **kwargs: Any) -> Awaitable[Any]:
        print('args', kwargs)
        tenant_id = settings.TENANT_ID
        audience = settings.AUDIENCE
        print('tenant_id', tenant_id)
        print('audience', audience)
        # return await func(*args, **kwargs)
        request: Request = kwargs["request"]

        # if SETTINGS.OFFLINE_USER is not None:
        #     request.state.user_id = SETTINGS.OFFLINE_USER
        # else:
        # request.state.user_id = DEFAULT_USER

        # if IS_OFFLINE:
        #     return await func(*args, **kwargs)

        # user_id = request.session.get("user_id", None)
        # if user_id is not None:
        #     request.state.user_id = user_id
        #     return await func(*args, **kwargs)

        logging.debug(f"Calling {func.__name__} with auth.")
        token = get_token_auth_header(request)

        jwks_url = settings.JWKS_URL
        # jwks_url = f"https://criticalplayground.b2clogin.com/criticalplayground.onmicrosoft.com/b2c_1_defaultsigninsignup2/discovery/v2.0/keys" #f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        # issuer_url = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        # issuer_url = f"https://{tenant_name}.b2clogin.com/{tenant_name}.onmicrosoft.com/{user_flow}/v2.0"
        # issuer_url = f"https://criticalplayground.b2clogin.com/287da62e-94fc-4504-b36e-f59ea81ca115/v2.0/"
        # issuer_url = f"https://criticalplayground.b2clogin.com/criticalplayground.onmicrosoft.com/b2c_1_defaultsigninsignup2/v2.0"
        issuer_url = f"https://criticalplayground.b2clogin.com/{tenant_id}/v2.0/"
        jwks_client = PyJWKClient(
            jwks_url,
        )
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        print(signing_key)
        try:
            # Decode without verifying signature to inspect claims
           
            decoded_payload = jwt.decode(
                token,
                signing_key.key,
                verify=True,
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer_url,
            )

        except jwt.ExpiredSignatureError:
            # Add logging
            print('ExpiredSignatureError')
            raise HTTPException(
                status_code=401,
                detail="Expired signature. Please obtain a new token.",
            )
        except jwt.DecodeError as ex:
            # Add logging
            print('DecodeError')
            raise HTTPException(
                status_code=401, detail="Unable to decode authentication token."
            )
        except Exception as ex:
            # Add logging
            print('General Exception', ex)
            raise HTTPException(
                status_code=401, detail="Unable to parse authentication token."
            )
        
        # print('decoded_payload', decoded_payload)
        user_email = get_user_info(decoded_payload)
        user_id = decoded_payload.get("oid", None)
        # print('user_id', user_id)
        # user_data = "tempuser"
        request.state.email = user_email
        request.state.user_id = user_id #normalize_text(email)
        return await func(*args, **kwargs)
    







# public string GetAccountId(ClaimsIdentity userIdentity)
# 		{
# 			var accountIdClaim = userIdentity.Claims.FirstOrDefault(c => c.Type == "http://schemas.microsoft.com/identity/claims/objectidentifier");
# 			if (accountIdClaim == null)
# 			{
# 				throw new ArgumentException("The user identity does not contain a valid account ID claim.");
# 			}
# 			return accountIdClaim.Value;
# 		}













        # # request.session["user_id"] = request.state.user_id
        # if SETTINGS.OFFLINE_USER is None:
        #         user_data = get_user(request)
        #     if "email" not in user_data:
        #         raise HTTPException(status_code=401, detail="Claims not found.")
        #     email = user_data["email"]
        #     if email is not None:
        #         request.state.user_id = normalize_text(email)
        #         request.session["user_id"] = request.state.user_id
        # return await func(*args, **kwargs)
        # raise HTTPException(status_code=401, detail="Unable to find appropriate key.")
        

        # jwks_url = settings.jwks_url
        # jwks = requests.get(
        #     jwks_url
        #     # f"{SETTINGS.AUTH_BASE_URL}/{SETTINGS.JWKS_ENDPOINT}", verify=False
        # ).json()
        # unverified_header = jwt.get_unverified_header(token)
        # rsa_key = {}
        # for key in jwks["keys"]:
        #     if key["kid"] == unverified_header["kid"]:
        #         rsa_key = key
        #         break
        # if rsa_key:
        #     try:
        #         jwt.decode(  # NOQA: F841
        #             token,
        #             rsa_key,
        #             algorithms=[SETTINGS.ALGORITHMS],
        #             audience=SETTINGS.AUTH_BASE_URL,
        #             issuer=SETTINGS.AUTH_BASE_URL,
        #         )
        #     except jwt.ExpiredSignatureError:
        #         raise HTTPException(status_code=401, detail="token is expired")
        #     except jwt.JWTClaimsError:
        #         raise HTTPException(
        #             status_code=401,
        #             detail="incorrect claims, please check the audience and issuer",
        #         )
        #     except Exception:
        #         raise HTTPException(
        #             status_code=401, detail="Unable to parse authentication token."
        #         )
        #     if SETTINGS.OFFLINE_USER is None:
        #         user_data = get_user(request)
        #         if "email" not in user_data:
        #             raise HTTPException(status_code=401, detail="Claims not found.")
        #         email = user_data["email"]
        #         if email is not None:
        #             request.state.user_id = normalize_text(email)
        #             request.session["user_id"] = request.state.user_id
        #     return await func(*args, **kwargs)
        # raise HTTPException(status_code=401, detail="Unable to find appropriate key.")

    wrapper.__signature__ = inspect.Signature(  # type: ignore
        parameters=[
            # Skip *args and **kwargs from wrapper parameters:
            *filter(
                lambda p: p.kind
                not in (
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
