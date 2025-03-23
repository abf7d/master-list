from sqlalchemy.orm import Session
from db_init.schemas import User
from datetime import datetime
import logging
from typing import Optional
import uuid

logger = logging.getLogger("repositories.user_repository")

class UserRepo:
    """Repository handling data access operations for User entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_oauth_id(self, oauth_id: str) -> Optional[User]:
        """Get a user by their OAuth ID"""
        return self.db.query(User).filter(User.oauth_id == oauth_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get a user by their internal ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create(self, oauth_id: str, email: str, name: str) -> User:
        """Create a new user"""
        user = User(
            oauth_id=oauth_id,
            email=email,
            name=name,
            created_at=datetime.utcnow()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_email(self, user: User, new_email: str) -> User:
        """Update a user's email"""
        user.email = new_email
        self.db.commit()
        self.db.refresh(user)
        return user