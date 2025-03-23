from typing import Dict, Any, Optional

class TokenUtils:
    """Utility functions for handling token data"""
    
    @staticmethod
    def extract_email_from_token(decoded_token: Dict[str, Any]) -> Optional[str]:
        """
        Extract email from decoded token
        
        Args:
            decoded_token: The JWT token payload as a dictionary
            
        Returns:
            The user's email or None if not found
        """
        if not decoded_token:
            return None
            
        # Check emails claim (most common in Azure B2C tokens)
        if "emails" in decoded_token:
            emails = decoded_token.get("emails", [])
            if emails and len(emails) > 0:
                return emails[0]
        
        # Check email claim (alternative)
        if "email" in decoded_token:
            return decoded_token["email"]
            
        return None
    
    @staticmethod
    def extract_user_info(decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all available user information from token and claims
        
        Args:
            decoded_token: The JWT token payload as a dictionary
            claims: Additional claims from an external service (optional)
            
        Returns:
            Dictionary containing user information
        """
        info = {}
        
        # Extract from token
        if decoded_token:
            # Get OAuth ID
            if "oid" in decoded_token:
                info["oauth_id"] = decoded_token["oid"]
                
            # Get email
            email = TokenUtils.extract_email_from_token(decoded_token)
            if email:
                info["email"] = email
                
            # Get name
            # if "name" in decoded_token:
            #     info["name"] = decoded_token["name"]
            info["name"] = TokenUtils.extract_name_from_token(decoded_token)
                
        return info
    
    @staticmethod
    def extract_name_from_token(decoded_token):
    # Try to get full name
        if "name" in decoded_token:
            return decoded_token["name"]
        
        # Try to combine given_name and family_name
        given_name = decoded_token.get("given_name")
        family_name = decoded_token.get("family_name")
        if given_name and family_name:
            return f"{given_name} {family_name}"
        elif given_name:
            return given_name
        elif family_name:
            return family_name
        
        # Check for displayName
        if "displayName" in decoded_token:
            return decoded_token["displayName"]
        
        return None