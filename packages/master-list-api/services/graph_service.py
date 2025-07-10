from typing import List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
import json

from msal import ConfidentialClientApplication
import requests
from fastapi import HTTPException
from core.config import settings

@dataclass
class Claim:
    type: str
    value: str
    value_type: str
    issuer: str

class GraphService:
    def __init__(self):
        self.tenant_id = settings.TENANT_ID
        self.graph_base_url = "https://graph.microsoft.com/v1.0/"
        self.logger = logging.getLogger(__name__)

    async def get_claims(self, user_id: str) -> List[Claim]:
        """
        Get claims for a user from Microsoft Graph API.
        
        Args:
            user_identity: Dictionary containing user claims/identity information
            
        Returns:
            List of Claim objects containing group memberships
        """
        client_id = settings.AZURE_AD_CLIENT_ID
        client_secret = settings.AZURE_AD_CLIENT_SECRET

        try:
            # Create MSAL Confidential Client
            confidential_client = ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}"
            )

            # Acquire token for Microsoft Graph
            auth_result = confidential_client.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )

            if "access_token" not in auth_result:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to acquire token for Microsoft Graph"
                )

            # Build the Graph API request
            api_url = f"{self.graph_base_url}users/{user_id}/transitiveMemberOf"
            headers = {
                "Authorization": f"Bearer {auth_result['access_token']}"
            }

            response = requests.get(api_url, headers=headers)

            # Handle API errors
            if not response.ok:
                error_response = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "code": "12-U8-3201",
                    "message": "There was an issue getting claims.",
                    "title": "WebException Occurred"
                }

                self.logger.error(
                    "Error getting claims from Microsoft Graph: %s", 
                    response.text
                )
                raise HTTPException(
                    status_code=500,
                    detail=json.dumps(error_response, indent=2)
                )

            # Parse response content
            groups_result = response.json()
            
            group_claims = []
            for group in groups_result.get("value", []):
                claim_type = (
                    group.get("@odata.type", "").split(".")[-1].lower() 
                    or "group"
                )
                group_claims.append(
                    Claim(
                        type=claim_type,
                        value=group.get("displayName", "Unknown"),
                        value_type="string",
                        issuer="https://graph.microsoft.com/"
                    )
                )

            return group_claims

        except Exception as ex:
            self.logger.error(
                "An exception occurred while getting claims from Microsoft Graph",
                exc_info=ex
            )
            raise

