from datetime import datetime
from typing import List, Optional
from uuid import UUID
import uuid
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db_init.schemas import Note, Tag, NoteItem, NoteItemList
from models.models import NoteItem as NoteItemModel, ResponseData
from models.models import CreateNoteGroup, MoveNoteGroup, NoteCreation, NoteEntry, NoteGroupResponse, NoteItemsResponse, TagEntry, TagResponse, NoteResponse
from sqlalchemy import and_, select, delete, tuple_, update
from sqlalchemy import func, case
from .util_service import UtilService


class ItemService:
    def __init__(self, db: Session):
        self.db = db
        self.utils = UtilService(db)
        

    def move_note_items(self, note_group: MoveNoteGroup, user_id: UUID) -> ResponseData:
        """
        Move note items to a new list or tag.
        
        Args:
            note_group: MoveNoteGroup object containing the items to move
            user_id: UUID of the user performing the move
        """
        if note_group.move_type is 'list':
            self.move_note_items_to_list(note_group, user_id)
            max_page = note_group.current_page
        elif note_group.move_type is 'page':
            max_page = self.move_note_items_to_page(note_group, user_id)
        return ResponseData(
            message="Note items moved successfully",
            data = {
                "max_page": max_page
            },
            error=None
        )
        
    def move_note_items_to_page(self, note_group: MoveNoteGroup, user_id: UUID) -> int:
        """
        Move note items to a new page (list).
        
        Args:
            note_group: MoveNoteGroup object containing the items to move
            user_id: UUID of the user performing the move
        """
        # Validate the note group
        if not note_group or not note_group.moved_state:
            raise HTTPException(status_code=400, detail="Invalid note group data")
        
        # Get the parent ID and type from the note group
        parent_id = note_group.list_id
        parent_list_type = note_group.list_type
        state = note_group.moved_state
        
        print('move_note_items_to_page')
        createGroupCurrent = CreateNoteGroup(
            parent_tag_id=parent_id,
            parent_list_type=parent_list_type,
            items=state.filtered,
            page=note_group.current_page 
        )
        
        self.update_note_items(createGroupCurrent, user_id=user_id, origin_type=parent_list_type)
        get_max_page = self.utils.get_max_page(parent_id, parent_list_type)
        new_page = get_max_page + 1
        
        createGroup = CreateNoteGroup(
            parent_tag_id=parent_id,
            parent_list_type=parent_list_type,
            items=state.moved,
            page=new_page,  # Set the new page number
        )
        self.update_note_items(createGroup, user_id=user_id, origin_type=parent_list_type)
        
        return new_page
        
    def move_note_items_to_list(self, note_group: MoveNoteGroup, user_id: UUID) -> None:
        """
        Move note items to a new list or tag.
        
        Args:
            note_group: MoveNoteGroup object containing the items to move
            user_id: UUID of the user performing the move
        """
        # Validate the note group
        if not note_group or not note_group.moved_state:
            raise HTTPException(status_code=400, detail="Invalid note group data")
        
        # Get the parent ID and type from the note group
        parent_id = note_group.list_id
        parent_list_type = note_group.list_type
        state = note_group.moved_state
        
        # Save the title for the new list or tag
        # self._save_title(parent_list_type, parent_id, note_group.tag_name)
        
        # need to look up the tag name to get the tag id
        tag_id = None
        tag_query = select(Tag).where(Tag.name == note_group.tag_name) #, Tag.created_by == user_id)
        tag = self.db.execute(tag_query).scalars().first()
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag '{note_group.tag_name}' not found for user {user_id}")
        tag_id = tag.id
        
        
        createGroupCurrent = CreateNoteGroup(
            parent_tag_id=parent_id,
            parent_list_type=parent_list_type,
            items=state.filtered
        )
        response_filtered = self.update_note_items(createGroupCurrent, user_id=user_id, origin_type=parent_list_type)
        
        
        new_tag_item_response = self.get_note_items(list_id=tag_id, user_id=user_id, list_type="tag")
        for item in state.moved:
            item.creation_list_id = None
            item.creation_type = None
            item.id = None
        # new_tag_items.data['notes'] = state.moved   
        createGroup = CreateNoteGroup(
            parent_tag_id=tag_id,
            parent_list_type='tag',
            items=[]
        )
        items = new_tag_item_response.data['notes']
        for item in items:
            createGroup.items.append(
                NoteItemModel(
                    content=item.content,
                    id=item.id,
                    tags=item.tags,
                    creation_list_id=item.creation_list_id,
                    
                    creation_type=item.creation_type,
                    position=None ,
                    origin_sort_order=item.origin_sort_order,          
            ))
        createGroup.items.extend(state.moved)
        response_moved = self.update_note_items(createGroup, user_id=user_id, origin_type="tag")
        
    
    def update_note_items(self, note_group: CreateNoteGroup, user_id: UUID, origin_type: str = "note") -> NoteGroupResponse:
        parent_id = note_group.parent_tag_id
        parent_list_type = note_group.parent_list_type if note_group.parent_list_type is not None else origin_type
        title = note_group.parent_list_title
        
        self._save_title(origin_type, parent_id, title)
        
        # First, handle deletion of items no longer in the list (this has changed to delete all items and then add the new ones)
        self._delete_existing_items(note_group, parent_id, parent_list_type, note_group.page)
        
        # Categorize items as new or existing (no longer categorizes, just maps all items to sort order)
        new_items = self._initialize_note_items(note_group, parent_id, parent_list_type)
        
        # Get tag mappings
        tag_ids_by_name = self._get_tag_name_id_map(note_group)
        
        # Process new items
        new_created_items, new_associations = self._save_note_items(
            new_items, tag_ids_by_name, parent_id, parent_list_type, user_id, note_group.page
        )
        
        # # Combine results (no longer gets existing items)
        created_note_items = new_created_items #existing_updated_items + new_created_items
        associations = new_associations # existing_associations + new_associations
        
        # Commit changes
        self.db.commit()
        
        return {
            "created_note_items": created_note_items,
            "associations": associations
        }
        
    def _save_title(self, origin_type: str, parent_id: UUID, title: str):
        """
        Save the title for a note.
        
        Args:
            origin_type: Type of origin list ("tag" or "note")
            parent_id: UUID of the parent
            title: Title to save
            
        Returns:
            None
        """
        if origin_type == "note" and parent_id and title is not None:
            # Update the title directly with a SQL update statement
            self.db.query(Note).filter(Note.id == parent_id).update({
                "title": title,
                "updated_at": datetime.utcnow()
            })
        
    def _delete_existing_items(self, note_group: CreateNoteGroup, parent_id: UUID, list_type: str, page: int | None = None):
        """
        Delete items that exist in the database but are not in the provided note_group.items list.
        This will delete both the NoteItem entries and their associated NoteItemList records.
        
        Args:
            note_group: CreateNoteGroup object containing current items
            parent_id: UUID of the parent (tag or note)
            list_type: Type of list ("tag" or "note")
        """
        if not parent_id:
            return  # We can't determine which items to delete without a parent_id
        
        # Get IDs of items that should be kept (none should be kept becasue of the new way we are doing it)
        # item_ids_to_keep = {item.id for item in note_group.items if item.id is not None}
        
        # Query to find all note items currently associated with this parent
        query = (
            self.db.query(NoteItem.id)
            .join(NoteItemList, NoteItem.id == NoteItemList.note_item_id)
            .filter(
                NoteItemList.list_id == parent_id,
                NoteItemList.list_type == list_type,
                NoteItemList.page == page 
            )
        )
        
        existing_item_ids = [row[0] for row in query.all()]
        
        # Find items that need to be deleted
        item_ids_to_delete = set(existing_item_ids) # - item_ids_to_keep
        
        if item_ids_to_delete:
            # First delete associations in note_item_lists
            self.db.query(NoteItemList).filter(
                NoteItemList.note_item_id.in_(item_ids_to_delete)
            ).delete(synchronize_session=False)
            
            # Then delete the note items themselves
            self.db.query(NoteItem).filter(
                NoteItem.id.in_(item_ids_to_delete)
            ).delete(synchronize_session=False)
    
    def _initialize_note_items(self, note_group: CreateNoteGroup, parent_id: UUID, parent_list_type: str):
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
        # existing_items = []
        # existing_item_ids = []
        
        for i, item in enumerate(note_group.items):
            data = {'data': item, 'order': i}
            # if item.creation_list_id is None or item.id is None:
                # This is a new item
            item.creation_list_id = item.creation_list_id or parent_id
            item.creation_type = item.creation_type or parent_list_type
            new_items.append(data)
            # else:
            #     # This is an existing item
            #     existing_items.append(data)
            #     existing_item_ids.append(item.id)
        
        return new_items #, existing_items, existing_item_ids
    
    
    def _get_tag_name_id_map(self, note_group: CreateNoteGroup):
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
            names = [tag.name for tag in item.tags]
            all_tag_names.update(names)
        
        # Then query the database once to get all tag IDs
        tag_ids_by_name = {}
        if all_tag_names:
            tags_query = select(Tag.id, Tag.name).where(
                Tag.name.in_(list(all_tag_names))
            )
            tag_results = self.db.execute(tags_query).fetchall()
            tag_ids_by_name = {tag_name: tag_id for tag_id, tag_name in tag_results}
        
        return tag_ids_by_name
    
    
    def _save_note_items(self, new_items, tag_ids_by_name, parent_id, parent_list_type, user_id, page: str | None = None):
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
        highest_sort_orders = {}
        
        # Create all new note items
        for i, item_data in enumerate(new_items):
            item = item_data['data']
            parent_sort_order = item_data['order']
            position = item.position if item.position is not None else parent_sort_order
            
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
            # This is for the sort orider of the note item on the parent/this list
            parent_sort_order = item_data['order']
            
            is_origin = item.creation_list_id == parent_id and item.creation_type == parent_list_type
            
            # Create parent association
            if parent_id:
                parent_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=parent_id,
                    list_type=parent_list_type,
                    is_origin=is_origin,
                    sort_order=parent_sort_order,
                    page=page  
                )
                self.db.add(parent_association)
                new_associations.append(parent_association)
            
            # Create tag associations
            for i, tag in enumerate(item.tags):
                tag_name = tag.name
                if tag_name not in tag_ids_by_name:
                    continue
                    
                tag_id = tag_ids_by_name[tag_name]
                
                if tag_id == parent_id:
                    continue
                
                # Determine the sort_order value
                sort_order = tag.sort_order
                a_page = tag.page
                if sort_order is None:
                    # Check if we've already cached the highest sort order for this tag
                    if tag_id not in highest_sort_orders:
                        # Query the highest sort_order for this tag
                        max_query = (
                            self.db.query(func.coalesce(func.max(NoteItemList.sort_order), -1))
                            .filter(
                                NoteItemList.list_id == tag_id,
                                NoteItemList.list_type == 'tag'
                            )
                        )
                        highest_sort = max_query.scalar()
                        highest_sort_orders[tag_id] = highest_sort
                    
                    # Get the highest sort order and increment by 1
                    sort_order = highest_sort_orders[tag_id] + 1
                    # Update the cache with the new highest value
                    highest_sort_orders[tag_id] = sort_order
                
                tag_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=tag_id,
                    list_type='tag',
                    is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag',
                    sort_order=sort_order, # If sort order is None then we will have to get the tag count for that id in the NoteItemList table
                    page=a_page
                )
                self.db.add(tag_association)
                new_associations.append(tag_association)
            
            # Create origin association if different from parent
            # The origin association might not be on this list so saving the parent AND not a tag (like a note) cases
            # above wouldn't have saved the origin association, origin_id is persisted, not on this list 
            if item.creation_list_id and (item.creation_list_id != parent_id or item.creation_type != parent_list_type):
                
                origin_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=item.creation_list_id,
                    list_type=item.creation_type,
                    is_origin=True,
                    sort_order=item.origin_sort_order,
                    page=item.origin_page
                )
                self.db.add(origin_association)
                new_associations.append(origin_association)
        
        return created_items, new_associations
    
    