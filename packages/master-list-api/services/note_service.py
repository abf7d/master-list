from datetime import datetime
from typing import List, Optional
from uuid import UUID
import uuid
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db_init.schemas import Note, Tag, NoteItem, NoteItemList
from models.models import CreateNoteGroup, NoteCreation, NoteEntry, NoteGroupResponse, NoteItemsResponse, TagEntry, TagResponse, NoteResponse
from sqlalchemy import and_, select, delete, tuple_, update
from sqlalchemy import func, case


class NoteService:
    def __init__(self, db: Session):
        self.db = db

    # def create_notes_for_tag(self, tag_id: UUID, content_list: List[str]) -> NoteGroupResponse:
    #     """
    #     Create notes under an existing tag.
        
    #     Args:
    #         tag_id: UUID of the existing parent tag
    #         content_list: List of text content for each note
            
    #     Returns:
    #         NoteGroupResponse with the tag and created notes
            
    #     Raises:
    #         NoResultFound: If the tag_id doesn't exist
    #     """
    #     # Verify tag exists
    #     tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
    #     if not tag:
    #         raise NoResultFound(f"Tag with id {tag_id} not found")
        
    #     # Create notes
    #     notes = []
    #     for i, content_item in enumerate(content_list):
    #         note = Note(
    #             content=content_item,
    #             creation_tag_id=tag_id,
    #             sequence_number=i
    #         )
    #         self.db.add(note)
    #         notes.append(note)
        
    #     self.db.flush()
        
    #     # Create note-tag associations
    #     for note in notes:
    #         note_tag = NoteTag(
    #             note_id=note.id,
    #             tag_id=tag_id
    #         )
    #         self.db.add(note_tag)
        
    #     # Commit changes
    #     self.db.commit()
        
    #     # Refresh objects from DB to get all fields
    #     for note in notes:
    #         self.db.refresh(note)
        
    #     # Construct response
    #     tag_response = TagResponse(
    #         id=tag.id,
    #         name=tag.name,
    #         parent_id=tag.parent_id,
    #         created_at=tag.created_at
    #     )
        
    #     note_responses = []
    #     for note in notes:
    #         note_responses.append(
    #             NoteResponse(
    #                 id=note.id,
    #                 content=note.content,
    #                 created_at=note.created_at,
    #                 updated_at=note.updated_at,
    #                 creation_tag_id=note.creation_tag_id,
    #                 sequence_number=note.sequence_number,
    #                 tags=[tag_response]  # Each note has the parent tag
    #             )
    #         )
        
    #     return NoteGroupResponse(
    #         tag=tag_response,
    #         notes=note_responses
    #     )
    
    def update_items(self, note_group: CreateNoteGroup, user_id: UUID, origin_type: str = "note") -> NoteGroupResponse:
        """
        Update existing note items and create new ones for a given parent (list_id).
        This preserves the sort_order field for existing items.
        
        Args:
            note_group: CreateNoteGroup object containing note items and parent info
            user_id: UUID of the user making the update
            origin_type: Type of origin list ("tag" or "note"), default is "note"
            
        Returns:
            Dict containing created note_items and associations
        """
        parent_id = note_group.parent_tag_id
        parent_list_type = note_group.parent_list_type if note_group.parent_list_type is not None else origin_type
        
        # Categorize items as new or existing
        new_items, existing_items, existing_item_ids = self._categorize_items(note_group, parent_id, parent_list_type)
        
        # Get tag mappings
        tag_ids_by_name = self._get_tag_ids_map(note_group)
        
        # Handle existing items
        existing_assoc_map = {}
        if existing_item_ids:
            existing_assoc_map = self._get_existing_associations(existing_item_ids)
            
        # Process existing items and update them
        existing_updated_items, existing_associations = self._update_existing_items(
            existing_items, existing_assoc_map, tag_ids_by_name, parent_id, parent_list_type
        )
        
        # Process new items
        new_created_items, new_associations = self._create_new_items(
            new_items, tag_ids_by_name, parent_id, parent_list_type, user_id
        )
        
        # Combine results
        created_note_items = existing_updated_items + new_created_items
        associations = existing_associations + new_associations
        
        # Commit changes
        self.db.commit()
        
        return {
            "created_note_items": created_note_items,
            "associations": associations
        }

    def _categorize_items(self, note_group: CreateNoteGroup, parent_id: UUID, parent_list_type: str):
        """
        Categorize items as new or existing.
        
        Args:
            note_group: CreateNoteGroup object
            parent_id: UUID of the parent
            parent_list_type: Type of the parent list
            
        Returns:
            Tuple of (new_items, existing_items, existing_item_ids)
        """
        new_items = []
        existing_items = []
        existing_item_ids = []
        
        for i, item in enumerate(note_group.items):
            data = {'data': item, 'order': i}
            if item.creation_list_id is None:
                # This is a new item
                item.creation_list_id = item.creation_list_id or parent_id
                item.creation_type = item.creation_type or parent_list_type
                new_items.append(data)
            else:
                # This is an existing item
                existing_items.append(data)
                existing_item_ids.append(item.id)
        
        return new_items, existing_items, existing_item_ids

    def _get_tag_ids_map(self, note_group: CreateNoteGroup):
        """
        Get a map of tag names to tag IDs.
        
        Args:
            note_group: CreateNoteGroup object
            
        Returns:
            Dict mapping tag names to tag IDs
        """
        # Pre-fetch all tag names to IDs to avoid multiple queries
        all_tag_names = set()
        for item in note_group.items:
            all_tag_names.update(item.tags)
        
        # Then query the database once to get all tag IDs
        tag_ids_by_name = {}
        if all_tag_names:
            tags_query = select(Tag.id, Tag.name).where(
                Tag.name.in_(list(all_tag_names))
            )
            tag_results = self.db.execute(tags_query).fetchall()
            tag_ids_by_name = {tag_name: tag_id for tag_id, tag_name in tag_results}
        
        return tag_ids_by_name

    def _get_existing_associations(self, existing_item_ids):
        """
        Get existing NoteItemList associations for the given item IDs.
        
        Args:
            existing_item_ids: List of note item IDs
            
        Returns:
            Dict mapping (note_item_id, list_id, list_type) to association details
        """
        existing_associations_query = select(
            NoteItemList.list_id,
            NoteItemList.note_item_id,
            NoteItemList.list_type,
            NoteItemList.is_origin,
            NoteItemList.sort_order
        ).where(NoteItemList.note_item_id.in_(existing_item_ids))
        
        existing_associations = self.db.execute(existing_associations_query).fetchall()
        existing_assoc_map = {}
        
        # Create a map for quick lookup
        for list_id, note_item_id, list_type, is_origin, sort_order in existing_associations:
            key = (note_item_id, list_id, list_type)
            existing_assoc_map[key] = {
                'is_origin': is_origin,
                'sort_order': sort_order
            }
        
        return existing_assoc_map

    def _update_existing_items(self, existing_items, existing_assoc_map, tag_ids_by_name, parent_id, parent_list_type):
        """
        Update existing note items and their associations.
        
        Args:
            existing_items: List of existing items to update
            existing_assoc_map: Map of existing associations
            tag_ids_by_name: Map of tag names to tag IDs
            parent_id: UUID of the parent
            parent_list_type: Type of the parent list
            
        Returns:
            Tuple of (updated_items, new_associations)
        """
        updated_items = []
        new_associations = []
        
        for item_data in existing_items:
            item = item_data['data']
            order = item_data['order']
            
            # Update note item content and updated_at
            update_stmt = update(NoteItem).where(
                NoteItem.id == item.id
            ).values(
                content=item.content,
                updated_at=datetime.utcnow(),
                sequence_number=item.position if item.position is not None else order
            )
            self.db.execute(update_stmt)
            
            # Fetch the updated item to add to our result
            updated_item = self.db.execute(
                select(NoteItem).where(NoteItem.id == item.id)
            ).scalar_one()
            updated_items.append(updated_item)
            
            # Update parent association if it exists
            new_assocs = self._update_parent_association(
                item, updated_item.id, order, parent_id, parent_list_type, existing_assoc_map
            )
            new_associations.extend(new_assocs)
            
            # Update tag associations
            tag_assocs = self._update_tag_associations(
                item, updated_item.id, tag_ids_by_name, existing_assoc_map
            )
            new_associations.extend(tag_assocs)
            
            # Ensure origin association exists
            origin_assoc = self._ensure_origin_association(
                item, updated_item.id, existing_assoc_map
            )
            if origin_assoc:
                new_associations.append(origin_assoc)
        
        return updated_items, new_associations

    def _update_parent_association(self, item, item_id, order, parent_id, parent_list_type, existing_assoc_map):
        """
        Update the parent association for an item.
        
        Args:
            item: NoteItem data object
            item_id: UUID of the note item from the updated db item
            order: Order position
            parent_id: UUID of the parent
            parent_list_type: Type of the parent list
            existing_assoc_map: Map of existing associations
            
        Returns:
            List of new associations created
        """
        new_associations = []
        
        if not parent_id:
            return new_associations
        
        parent_key = (item_id, parent_id, parent_list_type)
        if parent_key in existing_assoc_map:
            # Update existing association
            is_origin = item.creation_list_id == parent_id and item.creation_type == parent_list_type
            sort_order = existing_assoc_map[parent_key]['sort_order']
            
            update_assoc_stmt = update(NoteItemList).where(
                and_(
                    NoteItemList.note_item_id == item_id,
                    NoteItemList.list_id == parent_id,
                    NoteItemList.list_type == parent_list_type
                )
            ).values(
                is_origin=is_origin,
                sort_order=order if sort_order is None else sort_order
            )
            self.db.execute(update_assoc_stmt)
        else:
            # Create new association
            parent_association = NoteItemList(
                note_item_id=item_id,
                list_id=parent_id,
                list_type=parent_list_type,
                is_origin=item.creation_list_id == parent_id and item.creation_type == parent_list_type,
                sort_order=order
            )
            self.db.add(parent_association)
            new_associations.append(parent_association)
        
        return new_associations

    def _update_tag_associations(self, item, item_id, tag_ids_by_name, existing_assoc_map):
        """
        Update tag associations for an item.
        
        Args:
            item: NoteItem data object
            item_id: UUID of the note item
            tag_ids_by_name: Map of tag names to tag IDs
            existing_assoc_map: Map of existing associations
            
        Returns:
            List of new associations created
        """
        new_associations = []
        
        # Get current tag IDs for this item
        current_tag_ids = [tag_ids_by_name[tag_name] for tag_name in item.tags if tag_name in tag_ids_by_name]
        
        # Delete tag associations that are no longer needed
        for (note_id, list_id, list_type) in existing_assoc_map:
            if note_id == item_id and list_type == 'tag' and list_id not in current_tag_ids:
                delete_assoc_stmt = delete(NoteItemList).where(
                    and_(
                        NoteItemList.note_item_id == note_id,
                        NoteItemList.list_id == list_id,
                        NoteItemList.list_type == 'tag'
                    )
                )
                self.db.execute(delete_assoc_stmt)
        
        # Create or update tag associations
        for tag_name in item.tags:
            if tag_name not in tag_ids_by_name:
                continue
            
            tag_id = tag_ids_by_name[tag_name]
            tag_key = (item_id, tag_id, 'tag')
            
            if tag_key in existing_assoc_map:
                # Update existing tag association
                is_origin = item.creation_list_id == tag_id and item.creation_type == 'tag'
                sort_order = existing_assoc_map[tag_key]['sort_order']
                
                update_tag_assoc_stmt = update(NoteItemList).where(
                    and_(
                        NoteItemList.note_item_id == item_id,
                        NoteItemList.list_id == tag_id,
                        NoteItemList.list_type == 'tag'
                    )
                ).values(
                    is_origin=is_origin,
                    sort_order=sort_order  # Preserve sort order
                )
                self.db.execute(update_tag_assoc_stmt)
            else:
                # Create new tag association
                tag_association = NoteItemList(
                    note_item_id=item_id,
                    list_id=tag_id,
                    list_type='tag',
                    is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag',
                    sort_order=None  # New associations don't have a sort order yet
                )
                self.db.add(tag_association)
                new_associations.append(tag_association)
        
        return new_associations

    def _ensure_origin_association(self, item, item_id, existing_assoc_map):
        """
        Ensure that the origin association exists for an item.
        
        Args:
            item: NoteItem data object
            item_id: UUID of the note item
            existing_assoc_map: Map of existing associations
            
        Returns:
            New association if created, None otherwise
        """
        if not item.creation_list_id:
            return None
        
        origin_key = (item_id, item.creation_list_id, item.creation_type)
        if origin_key not in existing_assoc_map:
            origin_association = NoteItemList(
                note_item_id=item_id,
                list_id=item.creation_list_id,
                list_type=item.creation_type,
                is_origin=True,
                sort_order=None
            )
            self.db.add(origin_association)
            return origin_association
        
        return None

    def _create_new_items(self, new_items, tag_ids_by_name, parent_id, parent_list_type, user_id):
        """
        Create new note items and their associations.
        
        Args:
            new_items: List of new items to create
            tag_ids_by_name: Map of tag names to tag IDs
            parent_id: UUID of the parent
            parent_list_type: Type of the parent list
            user_id: UUID of the user
            
        Returns:
            Tuple of (created_items, new_associations)
        """
        created_items = []
        new_associations = []
        
        # Create all new note items
        for i, item_data in enumerate(new_items):
            item = item_data['data']
            order = item_data['order']
            position = item.position if item.position is not None else order
            
            # Create new note item
            new_note_item = NoteItem(
                content=item.content,
                created_by=user_id,
                sequence_number=position
            )
            
            self.db.add(new_note_item)
            created_items.append(new_note_item)
        
        # Flush to get generated IDs
        self.db.flush()
        
        # Create associations for new items
        for i, (item_data, note_item) in enumerate(zip(new_items, created_items)):
            item = item_data['data']
            order = item_data['order']
            
            # Create parent association
            if parent_id:
                parent_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=parent_id,
                    list_type=parent_list_type,
                    is_origin=item.creation_list_id == parent_id and item.creation_type == parent_list_type,
                    sort_order=order
                )
                self.db.add(parent_association)
                new_associations.append(parent_association)
            
            # Create tag associations
            for tag_name in item.tags:
                if tag_name not in tag_ids_by_name:
                    continue
                    
                tag_id = tag_ids_by_name[tag_name]
                
                tag_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=tag_id,
                    list_type='tag',
                    is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag',
                    sort_order=None
                )
                self.db.add(tag_association)
                new_associations.append(tag_association)
            
            # Create origin association if different from parent
            if item.creation_list_id and (item.creation_list_id != parent_id or item.creation_type != parent_list_type):
                origin_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=item.creation_list_id,
                    list_type=item.creation_type,
                    is_origin=True,
                    sort_order=None
                )
                self.db.add(origin_association)
                new_associations.append(origin_association)
        
        return created_items, new_associations
        
    # def update_items(self, note_group: CreateNoteGroup, user_id: UUID, origin_type: str = "note") -> NoteGroupResponse:
    #     """
    #     Update existing note items and create new ones for a given parent (list_id).
    #     This preserves the sort_order field for existing items.
        
    #     Args:
    #         note_group: CreateNoteGroup object containing note items and parent info
    #         user_id: UUID of the user making the update
    #         origin_type: Type of origin list ("tag" or "note"), default is "note"
            
    #     Returns:
    #         Dict containing created note_items and associations
    #     """
    #     parent_id = note_group.parent_tag_id
    #     parent_list_type = note_group.parent_list_type if note_group.parent_list_type is not None else origin_type
        
    #     # Categorize items as new or existing
    #     new_items = []
    #     existing_items = []
    #     existing_item_ids = []
        
    #     # Set creation id for all the items and categorize them
    #     for i, item in enumerate(note_group.items):
    #         data = {'data': item, 'order': i}
    #         if item.creation_list_id is None:
    #             # This is a new item
    #             item.creation_list_id = item.creation_list_id or parent_id
    #             item.creation_type = item.creation_type or parent_list_type
    #             new_items.append(data)
    #         else:
    #             # This is an existing item
    #             existing_items.append(data)
    #             existing_item_ids.append(item.id)
    #     print('existing items', existing_items)
    #     print('new tems', new_items)
        
    #     associations = []
    #     created_note_items = []
        
    #     # Pre-fetch all tag names to IDs to avoid multiple queries
    #     all_tag_names = set()
    #     for item in note_group.items:
    #         all_tag_names.update(item.tags)
        
    #     # Then query the database once to get all tag IDs
    #     tag_ids_by_name = {}
    #     if all_tag_names:
    #         tags_query = select(Tag.id, Tag.name).where(
    #             Tag.name.in_(list(all_tag_names))
    #         )
    #         tag_results = self.db.execute(tags_query).fetchall()
    #         tag_ids_by_name = {tag_name: tag_id for tag_id, tag_name in tag_results}
        
    #     # Handle existing items - update them and their associations
    #     if existing_item_ids:
    #         # Get current note item list associations for existing items
    #         existing_associations_query = select(
    #             NoteItemList.list_id,
    #             NoteItemList.note_item_id,
    #             NoteItemList.list_type,
    #             NoteItemList.is_origin,
    #             NoteItemList.sort_order
    #         ).where(NoteItemList.note_item_id.in_(existing_item_ids))
            
    #         existing_associations = self.db.execute(existing_associations_query).fetchall()
    #         existing_assoc_map = {}
            
    #         # Create a map for quick lookup
    #         for list_id, note_item_id, list_type, is_origin, sort_order in existing_associations:
    #             key = (note_item_id, list_id, list_type)
    #             existing_assoc_map[key] = {
    #                 'is_origin': is_origin,
    #                 'sort_order': sort_order
    #             }
            
    #         # Update existing items
    #         for item_data in existing_items:
    #             item = item_data['data']
    #             order = item_data['order']
                
    #             # Update note item content and updated_at
    #             update_stmt = update(NoteItem).where(
    #                 NoteItem.id == item.id
    #             ).values(
    #                 content=item.content,
    #                 updated_at=datetime.utcnow(),
    #                 sequence_number=item.position if item.position is not None else order
    #             )
    #             self.db.execute(update_stmt)
                
    #             # Fetch the updated item to add to our result
    #             updated_item = self.db.execute(
    #                 select(NoteItem).where(NoteItem.id == item.id)
    #             ).scalar_one()
    #             created_note_items.append(updated_item)
                
    #             # Update parent association - create if doesn't exist
    #             if parent_id:
    #                 parent_key = (item.id, parent_id, parent_list_type)
    #                 if parent_key in existing_assoc_map:
    #                     # Update existing association
    #                     is_origin = item.creation_list_id == parent_id and item.creation_type == parent_list_type
    #                     sort_order = existing_assoc_map[parent_key]['sort_order']
                        
    #                     update_assoc_stmt = update(NoteItemList).where(
    #                         and_(
    #                             NoteItemList.note_item_id == item.id,
    #                             NoteItemList.list_id == parent_id,
    #                             NoteItemList.list_type == parent_list_type
    #                         )
    #                     ).values(
    #                         is_origin=is_origin,
    #                         sort_order=order if sort_order is None else sort_order
    #                     )
    #                     self.db.execute(update_assoc_stmt)
    #                 else:
    #                     # Create new association
    #                     parent_association = NoteItemList(
    #                         note_item_id=item.id,
    #                         list_id=parent_id,
    #                         list_type=parent_list_type,
    #                         is_origin=item.creation_list_id == parent_id and item.creation_type == parent_list_type,
    #                         sort_order=order
    #                     )
    #                     self.db.add(parent_association)
    #                     associations.append(parent_association)
                
    #             # Handle tag associations
    #             current_tag_ids = [tag_ids_by_name[tag_name] for tag_name in item.tags if tag_name in tag_ids_by_name]
                
    #             # Delete tag associations that are no longer needed
    #             for (note_id, list_id, list_type) in existing_assoc_map:
    #                 if note_id == item.id and list_type == 'tag' and list_id not in current_tag_ids:
    #                     delete_assoc_stmt = delete(NoteItemList).where(
    #                         and_(
    #                             NoteItemList.note_item_id == note_id,
    #                             NoteItemList.list_id == list_id,
    #                             NoteItemList.list_type == 'tag'
    #                         )
    #                     )
    #                     self.db.execute(delete_assoc_stmt)
                
    #             # Create or update tag associations
    #             for tag_name in item.tags:
    #                 if tag_name not in tag_ids_by_name:
    #                     continue
                    
    #                 tag_id = tag_ids_by_name[tag_name]
    #                 tag_key = (item.id, tag_id, 'tag')
                    
    #                 if tag_key in existing_assoc_map:
    #                     # Update existing tag association
    #                     is_origin = item.creation_list_id == tag_id and item.creation_type == 'tag'
    #                     sort_order = existing_assoc_map[tag_key]['sort_order']
                        
    #                     update_tag_assoc_stmt = update(NoteItemList).where(
    #                         and_(
    #                             NoteItemList.note_item_id == item.id,
    #                             NoteItemList.list_id == tag_id,
    #                             NoteItemList.list_type == 'tag'
    #                         )
    #                     ).values(
    #                         is_origin=is_origin,
    #                         sort_order=sort_order  # Preserve sort order
    #                     )
    #                     self.db.execute(update_tag_assoc_stmt)
    #                 else:
    #                     # Create new tag association
    #                     tag_association = NoteItemList(
    #                         note_item_id=item.id,
    #                         list_id=tag_id,
    #                         list_type='tag',
    #                         is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag',
    #                         sort_order=None  # New associations don't have a sort order yet
    #                     )
    #                     self.db.add(tag_association)
    #                     associations.append(tag_association)
                
    #             # Ensure origin list association exists
    #             if item.creation_list_id:
    #                 origin_key = (item.id, item.creation_list_id, item.creation_type)
    #                 if origin_key not in existing_assoc_map:
    #                     origin_association = NoteItemList(
    #                         note_item_id=item.id,
    #                         list_id=item.creation_list_id,
    #                         list_type=item.creation_type,
    #                         is_origin=True,
    #                         sort_order=None
    #                     )
    #                     self.db.add(origin_association)
    #                     associations.append(origin_association)
        
    #     # Process new items (similar to original function)
    #     for i, item_data in enumerate(new_items):
    #         item = item_data['data']
    #         order = item_data['order']
    #         position = item.position if item.position is not None else order
            
    #         # Create new note item
    #         new_note_item = NoteItem(
    #             content=item.content,
    #             created_by=user_id,
    #             sequence_number=position
    #         )
            
    #         self.db.add(new_note_item)
    #         created_note_items.append(new_note_item)
        
    #     # Flush to get generated IDs for new items
    #     self.db.flush()
        
    #     # Create associations for new items
    #     for i, (item_data, note_item) in enumerate(zip(new_items, created_note_items[-len(new_items):])):
    #         item = item_data['data']
    #         order = item_data['order']
            
    #         # Create parent association
    #         if parent_id:
    #             parent_association = NoteItemList(
    #                 note_item_id=note_item.id,
    #                 list_id=parent_id,
    #                 list_type=parent_list_type,
    #                 is_origin=item.creation_list_id == parent_id and item.creation_type == parent_list_type,
    #                 sort_order=order
    #             )
    #             self.db.add(parent_association)
    #             associations.append(parent_association)
            
    #         # Create tag associations
    #         for tag_name in item.tags:
    #             if tag_name not in tag_ids_by_name:
    #                 continue
                    
    #             tag_id = tag_ids_by_name[tag_name]
                
    #             tag_association = NoteItemList(
    #                 note_item_id=note_item.id,
    #                 list_id=tag_id,
    #                 list_type='tag',
    #                 is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag',
    #                 sort_order=None
    #             )
    #             self.db.add(tag_association)
    #             associations.append(tag_association)
            
    #         # Create origin association if different from parent
    #         if item.creation_list_id and (item.creation_list_id != parent_id or item.creation_type != parent_list_type):
    #             origin_association = NoteItemList(
    #                 note_item_id=note_item.id,
    #                 list_id=item.creation_list_id,
    #                 list_type=item.creation_type,
    #                 is_origin=True,
    #                 sort_order=None
    #             )
    #             self.db.add(origin_association)
    #             associations.append(origin_association)
        
    #     # Commit changes
    #     self.db.commit()
        
    #     return {
    #         "created_note_items": created_note_items,
    #         "associations": associations
    #     }
    
    # Need to handle is_origin, need to persist when getting and need to update here when setting
    def update_note_items(self, note_group: CreateNoteGroup, user_id: UUID, origin_type: str = "note") -> NoteGroupResponse:
        """
        Update note items for a given parent (list_id).
        Steps:
        1. Delete existing associations between parent_id and note_items
        2. Delete existing note_items
        3. Create new note_items
        4. Create new associations
        
        Args:
            db: Database session
            note_group: CreateNoteGroup object containing note items and parent info
            user_id: UUID of the user making the update
            origin_type: Type of origin list ("tag" or "note"), default is "tag"
            
        Returns:
            Dict containing created note_items and associations
        """
        return self.update_items(note_group, user_id, origin_type) 
        parent_id = note_group.parent_tag_id
        parent_list_type = note_group.parent_list_type if note_group.parent_list_type is not None else origin_type
        
        new_items = []
        existing_items = []
        # set creation id for all the new items
        for i, item in enumerate(note_group.items):
            data = {'data': item, 'order': i}
            if item.creation_list_id == None:
                item.creation_list_id = parent_id
                item.creation_type = parent_list_type
                new_items.append(data)
            else:
                existing_items.append(data)
        # just update the existing note items, their association with this page, and add/delete new/old tags
        # drop then add the new note items, just delete other note items not in the either list
        # which means the deleted items
        if parent_id is None:
            # If no parent_id, we're creating completely new items
            # Skip deletion steps
            pass
        else:
            # Step 1: Find all note_item_ids associated with this parent_id
            note_item_ids_query = select(NoteItemList.note_item_id).where(
                and_(
                    NoteItemList.list_id == parent_id,
                    NoteItemList.list_type == parent_list_type
                )
            )
            note_item_ids = [row[0] for row in self.db.execute(note_item_ids_query).fetchall()]
            
            # TODO: Separate into function delete_note_items
            # TODO: This won't work because if you are on a tag and there is a note_item with an association to a note
            # TODO: the association with the origin will not be persisted to the frontend and when you delete the origin it will be done
            # So does that mean when you create a new note_item you will need to create an id in the frontend or do you just
            # tag it as new with a guid and when you save you need ot update the note_item with the new id.
            # It might be better to store the origin id on the note_item, but no becuase you would stil lhave the same 
            # problem pessisting the association
            # I thikn you have to mark the note_item as new and then when you save it you need to update the note_item with the new id 
            if note_item_ids:
                
                tag_associations_query = select(
                    NoteItemList.list_id,
                    NoteItemList.note_item_id,
                    NoteItemList.list_type
                ).where(
                    and_(
                        NoteItemList.note_item_id.in_(note_item_ids),
                        # NoteItemList.list_type == 'tag'
                    )
                )
                
                list_note_ids = [row for row in self.db.execute(tag_associations_query).fetchall()]
                # tag_ids = [row[0] for row in tag_note_ids]
                
                
                # Step 2: Delete all associations for these note_item_ids
                # Create a list of tuples from tag_note_ids
                tuple_pairs = [(list_id, note_item_id, list_type) for list_id, note_item_id, list_type in list_note_ids]

                # Use tuple_ to match against multiple columns at once
                delete_associations_stmt = delete(NoteItemList).where(
                    tuple_(NoteItemList.list_id, NoteItemList.note_item_id, NoteItemList.list_type).in_(tuple_pairs)
                )

                # Execute the delete statement
                self.db.execute(delete_associations_stmt)
                
                
                # Step 3: Delete all note_items
                delete_note_items_stmt = delete(NoteItem).where(
                    NoteItem.id.in_(note_item_ids)
                )
                self.db.execute(delete_note_items_stmt)
        
        # Pre-fetch all tag names to IDs to avoid multiple queries
        # First collect all unique tag names from all items
        all_tag_names = set()
        for item in note_group.items:
            all_tag_names.update(item.tags)
        
        # Then query the database once to get all tag IDs
        tag_ids_by_name = {}
        if all_tag_names:
            tags_query = select(Tag.id, Tag.name).where(
                Tag.name.in_(list(all_tag_names))
            )
            tag_results = self.db.execute(tags_query).fetchall()
            tag_ids_by_name = {tag_name: tag_id for tag_id, tag_name in tag_results}

        
        
        # Separate into function create_note_items
        # Step 4: Create new note_items and associations
        created_note_items = []
        
        # First, create all note items and collect them
        for i, item in enumerate(note_group.items):
            position = item.position if item.position is not None else i
            
            if item.id:
                # Use provided ID
                new_note_item = NoteItem(
                    id=item.id,
                    content=item.content,
                    created_by=user_id,
                    sequence_number=position
                )
            else:
                # Let the database generate the ID
                new_note_item = NoteItem(
                    content=item.content,
                    created_by=user_id,
                    sequence_number=position
                )
            
            self.db.add(new_note_item)
            created_note_items.append(new_note_item)
        
        # We need to flush to get the generated IDs
        self.db.flush()
        associations = []
        
        for item, note_item in zip(note_group.items, created_note_items):
            # Create parent association
            if parent_id:
                # For every note item on this list, save the association
                parent_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=parent_id,
                    list_type=parent_list_type,
                    is_origin=item.creation_list_id == parent_id and item.creation_type == parent_list_type 
                )
                self.db.add(parent_association)
                associations.append(parent_association)
            
            # Create tag associations
            # If there is another note item that is not on this list we don't worry about it, just the note_items
            # on this list and the tags
            for tag_name in item.tags:
                if tag_name not in tag_ids_by_name:
                    continue
                    
                tag_id = tag_ids_by_name[tag_name]
                
                #check if the association already exists as tags can populate the list and be associated with note-items
                match_found = any(i.note_item_id == note_item.id and
                    i.list_id == tag_id and
                    i.list_type == 'tag'
                    for i in associations
                )
                if not match_found:
                    tag_association = NoteItemList(
                        note_item_id=note_item.id,
                        list_id=tag_id,
                        list_type='tag',
                        is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag' #(origin_type == 'tag')
                    )
                    self.db.add(tag_association)
                    associations.append(tag_association)
            
            match_found = any(i.note_item_id == note_item.id and
                i.list_id == item.creation_list_id
                for i in associations
            )
            if not match_found:
                tag_association = NoteItemList(
                        note_item_id=note_item.id,
                        list_id=item.creation_list_id,
                        list_type=item.creation_type,
                        is_origin=True #(origin_type == 'tag')
                    )
                self.db.add(tag_association)
                associations.append(tag_association)
                
            
      
        
        # Commit changes
        self.db.commit()
        
       
        
        return {
            "created_note_items": created_note_items,
            "associations": associations
        }
    
    
    def get_note_items(self, list_id: UUID, user_id: UUID, list_type: str = "note") -> NoteItemsResponse:
        """
        Given a list_id and list_type, retrieve all NoteItems in that list and all Tags associated with those NoteItems.
        Orders NoteItems based on sort_order field in NoteItemList.
        
        Args:
            list_id: UUID of the list (Note or Tag)
            user_id: UUID of the user accessing the data
            list_type: Type of the list ('note' or 'tag')
            
        Returns:
            NoteItemsResponse containing ordered note_items and tags
        """
        list_name = None
        color_order = None
        if list_type == "tag":
            # Check if tag exists
            tag_query = select(Tag).where(Tag.id == list_id)
            tag = self.db.execute(tag_query).scalars().first()
            if not tag:
                return NoteItemsResponse(
                    data=None,
                    message=f"Tag with ID {list_id} not found",
                    error="Tag not found"
                )
            list_name = tag.name
            color_order = tag.creation_order
        elif list_type == "note":
            # Check if note exists
            note_query = select(Note).where(Note.id == list_id)
            note = self.db.execute(note_query).scalars().first()
            if not note:
                return NoteItemsResponse(
                    data=None,
                    message=f"Note with ID {list_id} not found",
                    error="Note not found"
                )
            list_name = note.title
        
        # Step 1: Get all note items with their sort_order for the given list
        note_items_query = select(
            NoteItem, 
            NoteItemList.sort_order, 
            NoteItemList.is_origin
        ).join(
            NoteItemList, 
            and_(
                NoteItem.id == NoteItemList.note_item_id,
                NoteItemList.list_id == list_id,
                NoteItemList.list_type == list_type
            )
        ).where(
            NoteItem.created_by == user_id
        ).order_by(
            # Order by sort_order if available, otherwise by sequence_number
            case(
                (NoteItemList.sort_order != None, NoteItemList.sort_order),
                else_=NoteItem.sequence_number
            )
        )
        
        note_items_results = self.db.execute(note_items_query).fetchall()
        note_item_ids = [result[0].id for result in note_items_results]
        
        # Step 2: Get all tag associations ordered by sort_order
        tag_associations_query = select(
            NoteItemList.list_id, 
            NoteItemList.note_item_id,
            NoteItemList.list_type,
            NoteItemList.is_origin,
            NoteItemList.sort_order
        ).where(
            NoteItemList.note_item_id.in_(note_item_ids)
        ).order_by(
            # Order associations by sort_order when available
            NoteItemList.sort_order.nullslast()
        )
        
        tag_associations = self.db.execute(tag_associations_query).fetchall()
        
        # Extract unique tag_ids from associations
        tag_ids = list(set([association[0] for association in tag_associations if association[2] == 'tag']))
        
        # Step 3: Get all tags for these tag_ids
        tags_query = select(Tag).where(
            Tag.id.in_(tag_ids)
        )
        tags = self.db.execute(tags_query).scalars().all()
        
        # Map tag id to name and other properties for easier conversion
        tag_map = {tag.id: {
            'name': tag.name,
            'parent_id': tag.parent_id,
            'created_at': tag.created_at,
            'order': tag.creation_order
        } for tag in tags}
        
        # Step 4: Construct the response with ordered note items
        note_responses = []
        note_item_to_associations = {}
        
        # Group associations by note_item_id for easier processing
        for tag_id, note_item_id, list_type, is_origin, sort_order in tag_associations:
            if note_item_id not in note_item_to_associations:
                note_item_to_associations[note_item_id] = []
            
            note_item_to_associations[note_item_id].append({
                'tag_id': tag_id,
                'list_type': list_type,
                'is_origin': is_origin,
                'sort_order': sort_order
            })
        
        # Process note items in the order they were fetched (by sort_order)
        for note_item, sort_order, is_list_origin in note_items_results:
            assigned_tags = []
            tag_data = []  # To store tag data with sort_order for ordering
            
            origin_id = None
            origin_type = None
            
            # Process associations for this note item
            associations = note_item_to_associations.get(note_item.id, [])
            
            for assoc in associations:
                tag_id = assoc['tag_id']
                assoc_list_type = assoc['list_type']
                is_origin = assoc['is_origin']
                assoc_sort_order = assoc['sort_order']
                
                # Check if this is the origin
                if is_origin:
                    origin_id = tag_id
                    origin_type = assoc_list_type
                
                # If it's a tag, add it to assigned_tags
                if assoc_list_type == 'tag' and tag_id in tag_map:
                    tag_data.append({
                        'name': tag_map[tag_id]['name'],
                        'sort_order': assoc_sort_order
                    })
            
            # Sort tags by sort_order if available
            tag_data.sort(
                key=lambda x: (x['sort_order'] is None, x['sort_order'])
            )
            
            # Extract just the names in order
            assigned_tags = [tag['name'] for tag in tag_data]
            
            note_responses.append(
                NoteResponse(
                    id=note_item.id,
                    content=note_item.content,
                    created_at=note_item.created_at,
                    updated_at=note_item.updated_at,
                    creation_list_id=origin_id,
                    creation_type=origin_type,
                    sequence_number=note_item.sequence_number,
                    tags=assigned_tags,
                    sort_order=sort_order  # Include sort_order in response if needed
                )
            )
        
        # Create tag responses in order
        tag_responses = []
        
        # Build a map of tags by note_item_id and their sort_orders
        tag_sort_orders = {}
        for tag_id, note_item_id, list_type, is_origin, sort_order in tag_associations:
            if list_type == 'tag' and tag_id in tag_map:
                if tag_id not in tag_sort_orders or (sort_order is not None and (tag_sort_orders[tag_id] is None or sort_order < tag_sort_orders[tag_id])):
                    tag_sort_orders[tag_id] = sort_order
        
        # Create tag responses with sort_order information
        for tag_id, tag_info in tag_map.items():
            tag_responses.append(
                TagEntry(
                    id=tag_id,
                    name=tag_info['name'],
                    parent_id=tag_info['parent_id'],
                    created_at=tag_info['created_at'],
                    order=tag_info['order'],
                    sort_order=tag_sort_orders.get(tag_id)  # Include sort_order if available
                )
            )
        
        # Sort tag responses by sort_order when available
        tag_responses.sort(key=lambda x: (x.sort_order is None, x.sort_order))
        
        return NoteItemsResponse(
            data={
                "notes": note_responses,  # Already ordered by sort_order from the query
                "tags": tag_responses,    # Ordered by sort_order
                "list_name": list_name,
                "list_type": list_type,
                "color_order": color_order
            },
            message="Success",
            error=None
        )
    
    
    
    
    
    
    
    # def get_note_items(self, list_id: UUID, user_id: UUID, list_type: str = "note") -> NoteItemsResponse:#db: Session, list_id: UUID, list_type: str) -> Dict[str, Any]:
    #     """
    #     Given a list_id and list_type, retrieve all NoteItems in that list and all Tags associated with those NoteItems.
        
    #     Args:
    #         db: Database session
    #         list_id: UUID of the list (Note or Tag)
    #         list_type: Type of the list ('note' or 'tag')
            
    #     Returns:
    #         Dict containing note_items and tags
    #     """
    #     list_name = None
    #     color_order = None
    #     if list_type == "tag":
    #         # Check if tag exists
    #         tag_query = select(Tag).where(Tag.id == list_id)
    #         tag = self.db.execute(tag_query).scalars().first()
    #         if not tag:
    #             return NoteItemsResponse(
    #                 data=None,
    #                 message=f"Tag with ID {list_id} not found",
    #                 error="Tag not found"
    #             )
    #         list_name = tag.name
    #         color_order = tag.creation_order
    #     elif list_type == "note":
    #         # Check if note exists
    #         note_query = select(Note).where(Note.id == list_id)
    #         note = self.db.execute(note_query).scalars().first()
    #         if not note:
    #             return NoteItemsResponse(
    #                 data=None,
    #                 message=f"Note with ID {list_id} not found",
    #                 error="Note not found"
    #             )
    #         list_name = note.title
            
    #     # Step 1: Get all note_item_ids for the given list_id and list_type
    #     note_item_ids_query = select(NoteItemList.note_item_id).where(
    #         and_(
    #             NoteItemList.list_id == list_id,
    #             NoteItemList.list_type == list_type
    #         )
    #     )
    #     note_item_ids = [row[0] for row in self.db.execute(note_item_ids_query).fetchall()]
        
    #     # Step 2: Get all note_items for these IDs
    #     note_items_query = select(NoteItem).where(
    #         NoteItem.id.in_(note_item_ids),
    #         NoteItem.created_by == user_id
    #     )
    #     note_items = self.db.execute(note_items_query).scalars().all()
    #     # note_items = [note_item in note_items_results]
        
    #     # Step 3: Get all tag associations (list_id and note_item_id pairs where list_type is 'tag')
    #     tag_associations_query = select(
    #         NoteItemList.list_id, 
    #         NoteItemList.note_item_id,
    #         NoteItemList.list_type,
    #         NoteItemList.is_origin
    #     ).where(
    #         and_(
    #             NoteItemList.note_item_id.in_(note_item_ids),
    #         )
    #     )
    #     tag_associations = self.db.execute(tag_associations_query).fetchall()
        
    #     # Extract unique tag_ids from associations
    #     tag_ids = list(set([association[0] for association in tag_associations if association[2] == 'tag']))
        
    #     # Step 4: Get all tags for these tag_ids
    #     tags_query = select(Tag).where(
    #         Tag.id.in_(tag_ids)
    #     )
    #     tags = self.db.execute(tags_query).scalars().all()
        
    #     # Map tag id to name for easier conversion
    #     tag_map = {tag.id: tag.name for tag in tags}  
       
            
    #     # Step 5: Construct the response    
    #     note_responses = []
    #     for note_item in note_items:
            
    #         assigned_tags = []
            
    #         origin_id = None
    #         origin_type = None
    #         for tag_id, note_item_id, list_type, is_origin in tag_associations:
                
    #             # if association is a tag and its note id matches this item
    #             if note_item_id == note_item.id and list_type == 'tag' and tag_id in tag_map:
    #                 name = tag_map[tag_id]
    #                 assigned_tags.append(name)
    #             if is_origin:
    #                 origin_id = tag_id
    #                 origin_type = list_type
            
    #         note_responses.append(
    #             NoteResponse(
    #                 id=note_item.id,
    #                 content=note_item.content,
    #                 created_at=note_item.created_at,
    #                 updated_at=note_item.updated_at,
    #                 creation_list_id=origin_id,
    #                 creation_type=origin_type,
    #                 sequence_number=note_item.sequence_number,
    #                 tags=assigned_tags
    #             )
    #         )
        
        
    #     tag_responses = [
    #         TagEntry(
    #             id=tag.id,
    #             name=tag.name,
    #             parent_id=tag.parent_id,
    #             created_at=tag.created_at,
    #             order=tag.creation_order
    #         )
    #         for tag in tags
    #     ]
    #     print(f"tag_responses: {str(tag_responses)}")
    #     return NoteItemsResponse(
    #         data={
    #             "notes": note_responses, 
    #             "tags": tag_responses,
    #             "list_name": list_name,
    #             "list_type": list_type,
    #             "color_order": color_order
    #         },
    #         message="Success",
    #         error=None
        # )
    

   

    # TODO: Move to tag repo, then call from here
    def create_tag(self, name: str, user_id:  Optional[UUID], parent_tag_id: Optional[UUID] = None) -> TagEntry:
        """
        Create a new tag with the specified name and optional parent.
        
        Args:
            name: Name for the tag
            parent_tag_id: Optional UUID of parent tag
            
        Returns:
            TagResponse for the created tag
        """
        
        # Check if a tag with this name already exists for this user
        existing_tag = self.db.query(Tag).filter(
            Tag.name == name,
            Tag.created_by == user_id
        ).first()
        
        if existing_tag:
            # Return a 409 Conflict status code with a clear message
            raise HTTPException(
                status_code=409,  # Conflict is appropriate for this case
                detail=f"A tag named '{name}' already exists for this user"
            )
        
        
        max_sequence = self.db.query(func.max(Tag.creation_order)).filter(Tag.created_by == user_id).scalar() or 0
        tag = Tag(
            name=name,
            parent_id=parent_tag_id,
            created_by=user_id,
            creation_order=max_sequence + 1
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        
        
        # todo: add id for the tag, return the same object as get tag so you can get id when creating a note
        # return TagCreation(
        # return tag.creation_order
        # return TagResponse(
        #     id=tag.id,
        #     name=tag.name,
        #     parent_id=tag.parent_id,
        #     created_at=tag.created_at
        # )
        return TagEntry(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at,
            order=tag.creation_order,
            sort_order=None
        )
        
        
        
    
    def create_note(self, user_id:  Optional[UUID]) -> TagEntry:
        """
        Create a new note with.
        
        Args:
            name: Name for the tag
            parent_tag_id: Optional UUID of parent tag
            
        Returns:
            TagResponse for the created tag
        """
        
        note = Note(
            created_by=user_id,
            
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return NoteCreation( # TODO: Change to NoteEntry
            id=note.id,
            created_at=note.created_at,
        )
    
    #TODO Delete all of the notes_tags that are linked to tag with the id from the selecated userid and name
    #TODO: Move to tag repo
    def delete_tag(self, name: str, user_id:  Optional[UUID]) -> int:
        """
        Delete a tag with the specified ID.
        
        Args:
            tag_id: UUID of the tag to delete
            user_id: UUID of the user requesting the deletion
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            HTTPException: If tag doesn't exist or user doesn't have permission
        """
        
        # Check if a tag with this name already exists for this user
        existing_tag = self.db.query(Tag).filter(
            Tag.name == name,
            Tag.created_by == user_id
        ).first()
        
        if not existing_tag:
            # Return a 409 Conflict status code with a clear message
            raise HTTPException(
                status_code=404,  # Conflict is appropriate for this case
                detail=f"A tag named '{name}' doesn't exist for this user"
            )
        
        # Delete the tag
        self.db.delete(existing_tag)
        self.db.commit()
        
        return True
        
        
    def get_tags(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        pageSize: int = 10,
        id: Optional[str] = None,
        parent_tag_id: Optional[UUID] = None
    ) -> Optional[List[TagEntry]]:
        """
        Get tags by user with optional filtering and pagination.

        Args:
            user_id: ID of the user
            query: Optional string to search tag names
            page: Page number (1-indexed)
            pageSize: Number of tags per page
            parent_tag_id: Optional UUID of parent tag

        Returns:
            A list of TagResponse models
        """

        # Base filters
        filters = [Tag.created_by == user_id]

        print('!!!! id: ', id)

        if id is not None:
            filters.append(Tag.id == id)
        if parent_tag_id is not None:
            filters.append(Tag.parent_id == parent_tag_id)

        # Optional search query (e.g., for autocomplete)
        if query:
            filters.append(Tag.name.ilike(f"{query}%"))  # Starts with; for partial match use `%{query}%`

        # Query with filters and pagination
        tags_query: Query = self.db.query(Tag).filter(and_(*filters))
        
        # Need to track usage statistics: https://claude.ai/chat/5f7f1716-0dca-4db7-9d21-fcf1de0c92a6
        tags_query = tags_query.order_by(
            case((Tag.name == query, 1), else_=0).desc(),
            func.length(Tag.name),
            Tag.name.asc()
        )  # Optional ordering
        tags_query = tags_query.offset((page - 1) * pageSize).limit(pageSize)

        tags = tags_query.all()

        tag_responses = []
        for tag in tags:
            
            tag_responses.append(
                TagEntry(
                    id=tag.id,
                    name=tag.name,
                    parent_id=tag.parent_id,
                    created_at=tag.created_at,
                    order=tag.creation_order,
                    sort_order=None
                )
            )
        
        return tag_responses
    
    def get_notes(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        pageSize: int = 10,
        id: Optional[str] = None,
        parent_tag_id: Optional[UUID] = None
    ) -> Optional[List[TagEntry]]:
            """
            Get notes by user with optional filtering and pagination.

            Args:
                user_id: ID of the user
                query: Optional string to search tag names
                page: Page number (1-indexed)
                pageSize: Number of tags per page
                parent_tag_id: Optional UUID of parent tag

            Returns:
                A list of TagResponse models
            """

            # Base filters
            filters = [Note.created_by == user_id]
            
            if id:
                filters.append(Note.id == id)

            # Optional search query (e.g., for autocomplete)
            if query:
                filters.append(Note.title.ilike(f"{query}%"))  # Starts with; for partial match use `%{query}%`

            # Query with filters and pagination
            notes_query: Query = self.db.query(Note).filter(and_(*filters))
            
            # Sort based on query presence
            if query:
                notes_query = notes_query.order_by(
                    case((Note.title == query, 1), else_=0).desc(),
                    func.length(Note.title),
                    Note.created_at.desc(),
                )
            else:
                notes_query = notes_query.order_by(Note.updated_at.desc())
            notes_query = notes_query.offset((page - 1) * pageSize).limit(pageSize)

            notes = notes_query.all()

            # Get all note IDs
            note_ids = [note.id for note in notes]
            
            # Using a window function to limit to top 2 NoteItems per note
            # This requires using raw SQL with the func module
            from sqlalchemy import func, text
            from sqlalchemy.orm import aliased

            # First, create a subquery that ranks NoteItems for each note
            ranked_items = text("""
                SELECT 
                    list_id, 
                    note_item_id, 
                    content,
                    ROW_NUMBER() OVER (PARTITION BY list_id ORDER BY sequence_number) as row_num
                FROM note_item_lists
                JOIN note_items ON note_item_lists.note_item_id = note_items.id
                WHERE 
                    list_id IN :note_ids AND
                    list_type = 'note' AND
                    note_items.created_by = :user_id
            """)
            
            # Then, select only rows where row_num <= 2
            top_items_query = text("""
                SELECT list_id, content
                FROM (
                    SELECT 
                        list_id, 
                        note_item_id, 
                        content,
                        ROW_NUMBER() OVER (PARTITION BY list_id ORDER BY sequence_number) as row_num
                    FROM note_item_lists
                    JOIN note_items ON note_item_lists.note_item_id = note_items.id
                    WHERE 
                        list_id IN :note_ids AND
                        list_type = 'note' AND
                        note_items.created_by = :user_id
                ) as ranked
                WHERE row_num <= 2
                ORDER BY list_id, row_num
            """)
            
            # Execute the query with parameters
            note_items_result = self.db.execute(
                top_items_query, 
                {"note_ids": tuple(note_ids) if note_ids else ('00000000-0000-0000-0000-000000000000',), 
                "user_id": user_id}
            ).fetchall()
            
            # Group NoteItems by note_id
            note_items_map = {}
            for list_id, content in note_items_result:
                if list_id not in note_items_map:
                    note_items_map[list_id] = []
                note_items_map[list_id].append(content)
            
            note_responses = []
            for i, note in enumerate(notes):
                # Get first 2 NoteItems for description
                description = note.description
                if not description and note.id in note_items_map:
                    # Items are already limited to 2 by the query
                    items = note_items_map[note.id]
                     # Check if there are any items
                    if len(items) > 0 and (len(items) == 1 and not items[0]) == False:
                        # Truncate each item if it's too long
                        truncated_items = [item[:100] + "..." if len(item) > 100 else item for item in items]
                        
                        # Format as HTML unordered list
                        list_items = "".join([f"<li>{item}</li>" for item in truncated_items])
                        description = f"<ul>{list_items}</ul>"
                    else:
                        # No items found, set description to None/null
                        description = None
                print('description', description)
                note_responses.append(
                    NoteEntry(
                        id=note.id,
                        title=note.title,
                        description=description,
                        created_at=note.created_at,
                        updated_at=note.updated_at,
                        order=i
                    )
                )
            
            return note_responses
    def get_notesOLD(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        pageSize: int = 10,
        id: Optional[str] = None,
        parent_tag_id: Optional[UUID] = None
    ) -> Optional[List[TagEntry]]:
        """
        Get notes by user with optional filtering and pagination.

        Args:
            user_id: ID of the user
            query: Optional string to search tag names
            page: Page number (1-indexed)
            pageSize: Number of tags per page
            parent_tag_id: Optional UUID of parent tag

        Returns:
            A list of TagResponse models
        """

        # Base filters
        filters = [Note.created_by == user_id]
        
        if id:
            filters.append(Note.id == id)
        # if parent_tag_id is not None:
            # filters.append(Tag.parent_id == parent_tag_id)

        # Optional search query (e.g., for autocomplete)
        if query:
            filters.append(Note.title.ilike(f"{query}%"))  # Starts with; for partial match use `%{query}%`

        # Query with filters and pagination
        notes_query: Query = self.db.query(Note).filter(and_(*filters))
        
        # Need to track usage statistics: https://claude.ai/chat/5f7f1716-0dca-4db7-9d21-fcf1de0c92a6
        # if query order by alphabetic otherwise get teh most recent
        if query:
            # If there's a search query, prioritize exact match, then sort by title
            notes_query = notes_query.order_by(
                case((Note.title == query, 1), else_=0).desc(),
                func.length(Note.title),
                Note.created_at.desc(),
            )
        else:
            # If no search query, show most recently updated first
            notes_query = notes_query.order_by(Note.updated_at.desc())
        notes_query = notes_query.offset((page - 1) * pageSize).limit(pageSize)

        notes = notes_query.all()

        note_responses = []
        for i, note in enumerate(notes):
            print('note', note)
            note_responses.append(
                NoteEntry  (
                    id=note.id,
                    title=note.title,
                    description=note.description,
                    created_at=note.created_at,
                    updated_at=note.updated_at,
                    order=i
                )
            )
        
        return note_responses
    
    

    def get_note_group_by_tag_id(self, tag_id: UUID) -> Optional[NoteGroupResponse]:
        """
        Get a note group by tag ID
        
        Args:
            tag_id: UUID of the tag
            
        Returns:
            NoteGroupResponse or None if tag not found
        """
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None
            
        notes = self.db.query(NoteItem).filter(NoteItem.creation_tag_id == tag_id).order_by(NoteItem.sequence_number).all()
        
        tag_response = TagResponse(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at
        )
        
        note_responses = []
        for note in notes:
            note_responses.append(
                NoteResponse(
                    id=note.id,
                    content=note.content,
                    created_at=note.created_at,
                    updated_at=note.updated_at,
                    creation_list_id=note.creation_tag_id,
                    sequence_number=note.sequence_number,
                    tags=[tag_response]
                )
            )
            
        return NoteGroupResponse(
            tag=tag_response,
            notes=note_responses
        )
        
    def update_tag_name(self, tag_id: UUID, new_name: str) -> TagResponse:
        """
        Update the name of an existing tag
        
        Args:
            tag_id: UUID of the tag to update
            new_name: New name for the tag
            
        Returns:
            Updated TagResponse
            
        Raises:
            NoResultFound: If the tag_id doesn't exist
        """
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise NoResultFound(f"Tag with id {tag_id} not found")
            
        tag.name = new_name
        self.db.commit()
        self.db.refresh(tag)
        
        return TagResponse(
            id=tag.id,
            name=tag.name,
            parent_id=tag.parent_id,
            created_at=tag.created_at
        )

# from fastapi import Depends
# from repos.notes_repo import NoteRepo
# from db_init.schemas import NoteCreate

# class NotesService:
#     def __init__(self, repo: NoteRepo = Depends()):
#         self.repo = repo
    
#     async def create_order(self, order: NoteCreate):
#         # Business logic, validation, etc.
#         return await self.repo.create(order)