# Repository
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional, Dict
from sqlalchemy.ext.declarative import declarative_base
from ..models import Tag
from ..models import TagResponse

Base = declarative_base()
class TagRepository:
    def __init__(self, db: Session):
        self.db = db
    
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