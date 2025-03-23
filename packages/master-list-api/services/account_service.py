import logging
from typing import Dict, Any, Optional
import uuid

from repos.user_repo import UserRepo
from db_init.schemas import User
from utils.token_utils import TokenUtils

logger = logging.getLogger("services.user_service")

class AccountService:
    """Service handling business logic for user management"""
    
    def __init__(self, user_repository: UserRepo):
        self.user_repository = user_repository
    
    def get_user_by_oauth_id(self, oauth_id: str) -> Optional[User]:
        """
        Get a user by their OAuth ID
        
        Args:
            oauth_id: The OAuth ID from the authentication provider
            
        Returns:
            The user if found, None otherwise
        """
        return self.user_repository.get_by_oauth_id(oauth_id)
    
    def get_or_create_user_from_token(self, 
                                      oauth_id: str, 
                                      decoded_token: Dict[str, Any], 
                                      claims: Dict[str, Any] = None) -> User:
        """
        Get a user by OAuth ID or create them using info from the token/claims
        
        Args:
            oauth_id: The OAuth ID from the authentication provider
            decoded_token: The decoded JWT token
            claims: Additional claims from external service (optional)
            
        Returns:
            Existing or newly created user
            
        Raises:
            ValueError: If email cannot be determined from token or claims
        """

        # Todo: check if autorized or an admin, don't add all users

        # Extract all user info from token and claims
        user_info = TokenUtils.extract_user_info(decoded_token)
        
        # Ensure we have an email
        if "email" not in user_info:
            logger.error(f"Could not determine email for user with OAuth ID: {oauth_id}")
            raise ValueError("Email not found in token or claims")
        
        email = user_info["email"]
        
        name = user_info["name"]

        # Try to get existing user
        user = self.user_repository.get_by_oauth_id(oauth_id)
        
        if not user:
            # User doesn't exist, create a new one
            logger.info(f"Creating new user with OAuth ID: {oauth_id}")
            try:
                user = self.user_repository.create(oauth_id, email, name)
                logger.info(f"Successfully created user with email: {email}")
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                # This might be a race condition - try to get the user again
                user = self.user_repository.get_by_oauth_id(oauth_id)
                if not user:
                    # If still not found, re-raise the exception
                    raise
        elif user.email != email:
            # User exists but email has changed, update it
            logger.info(f"Updating email for user {oauth_id} from {user.email} to {email}")
            try:
                user = self.user_repository.update_email(user, email)
                logger.info(f"Successfully updated email to: {email}")
            except Exception as e:
                logger.error(f"Error updating user email: {str(e)}")
                # This error shouldn't prevent the user from using the application
                pass
        
        return user
    
    def get_user_id_by_oauth_id(self, oauth_id: str) -> Optional[uuid.UUID]:
        """
        Get a user's internal ID by their OAuth ID
        
        This is useful for relating other entities to users
        
        Args:
            oauth_id: The OAuth ID from the authentication provider
            
        Returns:
            The user's internal UUID if found, None otherwise
        """
        user = self.user_repository.get_by_oauth_id(oauth_id)
        return user.id if user else None