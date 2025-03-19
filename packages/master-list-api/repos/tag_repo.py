# Repository
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional, Dict
from sqlalchemy.ext.declarative import declarative_base
from db_init.schemas import Tag
from db_init.schemas import TagResponse
import requests

Base = declarative_base()
class TagRepository:
    def __init__(self, db: Session):
        self.db = db
    
    # obsidian note taking app can connect via symantic links saves into markdonwn
    # start with trying this, create a tag
    def create_tag(db: Session, user_id: str, tag_name: str):
        """Creates a new tag and assigns ownership in OpenFGA."""

        OPENFGA_URL = '127.0.0.1:1234'
        STORE_ID = 'critical-notes'
        # Step 1: Create Tag in Database (UUID is auto-generated)
        new_tag = Tag(
            name=tag_name,
            created_by=user_id
        )
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)  # ✅ The UUID is now available from the database

        # Step 2: Assign Ownership in OpenFGA
        fga_payload = {
            "writes": [
                {
                    "tuple_key": {
                        "user": f"user:{user_id}",
                        "relation": "owner",
                        "object": f"tag:{new_tag.id}"
                    }
                }
            ]
        }

        headers = {"Content-Type": "application/json"}
        fga_response = requests.post(
            f"{OPENFGA_URL}/stores/{STORE_ID}/write",
            json=fga_payload,
            headers=headers
        )

        if fga_response.status_code != 200:
            print("Error setting OpenFGA permissions:", fga_response.json())

        return new_tag
    
    def create_tag(self, name: str, parent_id: Optional[UUID] = None) -> TagResponse:
        """Create a new tag"""
        # Check if tag with same name exists under the same parent
        existing_tag = self.db.query(Tag).filter(
            Tag.name == name,
            Tag.parent_id == parent_id
        ).first()
        
        if existing_tag:
            raise ValueError(f"Tag '{name}' already exists in this scope")
        
        tag = Tag(name=name, parent_id=parent_id)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return TagResponse.from_orm(tag)
    
    def get_tag(self, tag_id: UUID) -> Optional[TagResponse]:
        """Get a tag by ID"""
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        return TagResponse.from_orm(tag) if tag else None
    
    # def get_tag(db: Session, user_id: str, tag_id: str):
    #     """Fetches a tag if the user is either the owner or has view access via OpenFGA."""

    #     # Step 1: Fetch the Tag from the Database
    #     tag = db.query(Tag).filter(Tag.id == tag_id).first()

    #     if not tag:
    #         return None  # Tag not found

    #     # Step 2: If User is the Creator, Return Immediately
    #     if str(tag.created_by) == user_id:
    #         return tag  # Owner gets direct access ✅

    #     # Step 3: If Not Owner, Check OpenFGA for `can_view` Permission
    #     fga_payload = {
    #         "tuple_key": {
    #             "user": f"user:{user_id}",
    #             "relation": "can_view",
    #             "object": f"tag:{tag_id}"
    #         }
    #     }

    #     headers = {"Content-Type": "application/json"}
    #     fga_response = requests.post(
    #         f"{OPENFGA_URL}/stores/{STORE_ID}/check",
    #         json=fga_payload,
    #         headers=headers
    #     )

    #     if fga_response.status_code == 200 and fga_response.json().get("allowed"):
    #         return tag  # User has view access via OpenFGA ✅
    #     else:
    #         return None  # User does not have access 🚫
        
    
    def get_tags_by_parent(self, parent_id: Optional[UUID] = None) -> List[TagResponse]:
        """Get all tags under a parent (or top-level tags if parent_id is None)"""
        tags = self.db.query(Tag).filter(Tag.parent_id == parent_id).all()
        return [TagResponse.from_orm(tag) for tag in tags]
    
    def update_tag(self, tag_id: UUID, name: str) -> TagResponse:
        """Update a tag's name"""
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise ValueError(f"Tag with ID {tag_id} not found")
        
        # Check if new name would conflict with existing tag
        existing_tag = self.db.query(Tag).filter(
            Tag.name == name,
            Tag.parent_id == tag.parent_id,
            Tag.id != tag_id
        ).first()
        
        if existing_tag:
            raise ValueError(f"Tag '{name}' already exists in this scope")
        
        tag.name = name
        self.db.commit()
        self.db.refresh(tag)
        return TagResponse.from_orm(tag)
    
    




    def move_tag(self, tag_id: UUID, new_parent_id: Optional[UUID]) -> TagResponse:
        """Move a tag to a new parent"""
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise ValueError(f"Tag with ID {tag_id} not found")
        
        # Prevent moving a tag to be its own descendant
        if new_parent_id:
            current = self.db.query(Tag).filter(Tag.id == new_parent_id).first()
            while current and current.parent_id:
                if current.parent_id == tag_id:
                    raise ValueError("Cannot move tag to its own descendant")
                current = self.db.query(Tag).filter(Tag.id == current.parent_id).first()
        
        # Check for name conflicts in new location
        existing_tag = self.db.query(Tag).filter(
            Tag.name == tag.name,
            Tag.parent_id == new_parent_id,
            Tag.id != tag_id
        ).first()
        
        if existing_tag:
            raise ValueError(f"Tag '{tag.name}' already exists under the new parent")
        
        tag.parent_id = new_parent_id
        self.db.commit()
        self.db.refresh(tag)
        return TagResponse.from_orm(tag)
    
    def delete_tag(self, tag_id: UUID, recursive: bool = False):
        """
        Delete a tag. If recursive=True, also delete all child tags.
        Otherwise, raise an error if the tag has children.
        """
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise ValueError(f"Tag with ID {tag_id} not found")
        
        # Check for child tags
        children = self.db.query(Tag).filter(Tag.parent_id == tag_id).all()
        if children and not recursive:
            raise ValueError("Cannot delete tag with children. Use recursive=True to delete children as well.")
        
        if recursive:
            # Delete all descendants
            def delete_descendants(parent_id):
                children = self.db.query(Tag).filter(Tag.parent_id == parent_id).all()
                for child in children:
                    delete_descendants(child.id)
                    self.db.delete(child)
            
            delete_descendants(tag_id)
        
        # Delete the tag itself
        self.db.delete(tag)
        self.db.commit()
    
    def get_tag_hierarchy(self, root_id: Optional[UUID] = None) -> List[Dict]:
        """
        Get a hierarchical representation of tags.
        If root_id is provided, get hierarchy from that tag down.
        If root_id is None, get entire hierarchy from all top-level tags.
        """
        def build_hierarchy(parent_id: Optional[UUID]) -> List[Dict]:
            tags = self.db.query(Tag).filter(Tag.parent_id == parent_id).all()
            return [{
                'tag': TagResponse.from_orm(tag),
                'children': build_hierarchy(tag.id)
            } for tag in tags]
        
        if root_id:
            root_tag = self.db.query(Tag).filter(Tag.id == root_id).first()
            if not root_tag:
                raise ValueError(f"Tag with ID {root_id} not found")
            return [{
                'tag': TagResponse.from_orm(root_tag),
                'children': build_hierarchy(root_id)
            }]
        
        return build_hierarchy(None)