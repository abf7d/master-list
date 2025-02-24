from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Account:
    isAdmin: bool
    isAuthorized: bool
    name: Optional[str]
    emails: Optional[str]
    userName: Optional[str]
    id: str

class AccountMapper:
    def __init__(self):
        self.ADMIN_GROUP = "Site Admin"  # Replace with your actual admin group name
        self.AUTHORIZED_USER_GROUP = "Authorized User"  # Replace with your actual authorized group name

    def map_claims_to_account(self, claims: List[dict], user_identity: dict) -> Account:
        """
        Maps claims to an Account object.
        
        Args:
            claims: List of claims dictionaries
            user_identity: Dictionary containing user identity claims
            
        Returns:
            Account object populated with user information
        """
        # Find admin and authorized claims
        admin_claim = next((claim for claim in claims if claim.get('value') == self.ADMIN_GROUP), None)
        authorized_claim = next((claim for claim in claims if claim.get('value') == self.AUTHORIZED_USER_GROUP), None)
        
        # Extract user information from identity
        name = user_identity.get('name')
        emails = user_identity.get('emails')
        if isinstance(emails, list) and emails:
            emails = emails[0]  # Get first email if it's a list
            
        user_name = user_identity.get('name')
        
        # Get user ID - try multiple possible claim types
        user_id = user_identity.get('sub')  # NameIdentifier equivalent
        if not user_id:
            user_id = user_identity.get('oid')
            
        if not user_id:
            raise ValueError("Unable to find user ID in identity claims")
            
        # Create and return account
        return Account(
            isAdmin=(admin_claim is not None),
            isAuthorized=(authorized_claim is not None),
            name=name,
            emails=emails,
            userName=user_name,
            id=user_id
        )