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


class NoteService:
    def __init__(self, db: Session):
        self.db = db
        
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
        
    def get_max_page(self, parent_id: UUID, parent_list_type: str) -> int:
        """
        Get the maximum page number for a given parent ID and list type.
        
        Args:
            parent_id: UUID of the parent (tag or note)
            parent_list_type: Type of the parent list ('note' or 'tag')
            
        Returns:
            int: Maximum page number
        """
        if not parent_id or not parent_list_type:
            return 0
        # Query to get the maximum page number for the given parent ID and list type
        max_page_query = (
            self.db.query(func.max(NoteItemList.page))
            .filter(
                NoteItemList.list_id == parent_id,
                NoteItemList.list_type == parent_list_type
            )
        )
        max_page = max_page_query.scalar()
        return max_page if max_page is not None else 0
        
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
        get_max_page = self.get_max_page(parent_id, parent_list_type)
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
    
# try saving the filtered first to delete the items then try to save?
#     {
#     "moved_state": {
#         "moved": [
#             {
#                 "id": "cea7d443-1e3a-48d8-9e6a-25d887ac6720",
#                 "content": "six 6",
#                 "created_at": "2025-06-06T15:55:16.818903",
#                 "updated_at": "2025-06-06T15:55:16.818904",
#                 "creation_list_id": "39b86243-9a87-4559-8534-e6e4e40ab1b7",
#                 "creation_type": "note",
#                 "sequence_numb 1,
#                 "tags": [],
#                 "origin_sort_order": 1
#             },
#             {
#                 "id": "8aa381e0-0f86-4ee4-a7a0-160b0921613f",
#                 "content": "111111",
#                 "created_at": "2025-06-06T15:55:16.818912",
#                 "updated_at": "2025-06-06T15:55:16.818913",
#                 "creation_list_id": "39b86243-9a87-4559-8534-e6e4e40ab1b7",
#                 "creation_type": "note",
#                 "sequence_number": 2,
#                 "tags": [],
#                 "origin_sort_order": 2
#             }
#         ],
#         "filtered": [
#             {
#                 "id": "2593feb8-b3c2-43db-b46c-65788f7201cf",
#                 "content": "one 1",
#                 "created_at": "2025-06-06T15:55:16.818887",
#                 "updated_at": "2025-06-06T15:55:16.818893",
#                 "creation_list_id": "39b86243-9a87-4559-8534-e6e4e40ab1b7",
#                 "creation_type": "note",
#                 "sequence_number": 0,
#                 "tags": [
#                     {
#                         "id": "11111111-1111-1111-1111-111111111111",
#                         "name": "2",
#                         "sort_order": 25
#                     }
#                 ],
#                 "origin_sort_order": 0
#             },
#             {
#                 "id": "acf9251c-f7f0-46a5-8848-97a6198a85e0",
#                 "content": "4444",
#                 "created_at": "2025-06-06T15:55:16.818921",
#                 "updated_at": "2025-06-06T15:55:16.818922",
#                 "creation_list_id": "39b86243-9a87-4559-8534-e6e4e40ab1b7",
#                 "creation_type": "note",
#                 "sequence_number": 3,
#                 "tags": [],
#                 "origin_sort_order": 3
#             },
#             {
#                 "id": "7c0a7efe-3863-4d8e-943f-b091e78fb3d0",
#                 "content": "<br>",
#                 "created_at": "2025-06-06T15:55:16.818929",
#                 "updated_at": "2025-06-06T15:55:16.818930",
#                 "creation_list_id": "39b86243-9a87-4559-8534-e6e4e40ab1b7",
#                 "creation_type": "note",
#                 "sequence_number": 4,
#                 "tags": [],
#                 "origin_sort_order": 4
#             }
#         ]
#     },
#     "list_id": "39b86243-9a87-4559-8534-e6e4e40ab1b7",
#     "list_type": "note",
#     "tag_name": "2"
# }
    
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
    
    
    
    def get_note_items(self, list_id: UUID, user_id: UUID, list_type: str, page: int | None = None) -> NoteItemsResponse:
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
        if list_type not in ["note", "tag"]:
            return NoteItemsResponse(
                data=None,
                message="Invalid list type. Must be 'note' or 'tag'.",
                error="Invalid list type"
            )
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
                NoteItemList.list_type == list_type,
                NoteItemList.page == page
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
            NoteItemList.sort_order,
            NoteItemList.page
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
        # These are Tag objects, not the associations
        tag_map = {tag.id: {
            'name': tag.name,
            'parent_id': tag.parent_id,
            'created_at': tag.created_at,
            'order': tag.creation_order,
            # 'id' add tag id to the tag object
        } for tag in tags}
        
        # Step 4: Construct the response with ordered note items
        note_responses = []
        note_item_to_associations = {}
        this_list_order = {}
        
        # Group associations by note_item_id for easier processing
        for a_list_id, note_item_id, a_list_type, is_origin, sort_order, a_page in tag_associations:
            if note_item_id not in note_item_to_associations:
                note_item_to_associations[note_item_id] = []
            
            # save order for organizing the note_items, if you are on this list
            if list_id == str(a_list_id) and a_list_type == list_type:
                this_list_order[note_item_id] = sort_order
                
            # These are NoteItemLIst objects/associations
            note_item_to_associations[note_item_id].append({
                'list_id': a_list_id,
                'list_type': a_list_type,
                'is_origin': is_origin,
                'sort_order': sort_order,
                'page': a_page
            })
        
        # Process note items in the order they were fetched (by sort_order)
        # this is this lists associations, not others. So the note item's origin might be on a different list which may never hit the condition below and the origin id might be null
        # Check if origin id is on this list and then call out to retrieve it at the end for each note item
        for note_item, sort_order, is_list_origin in note_items_results:
            assigned_tags = []
            tag_data = []  # To store tag data with sort_order for ordering
            
            origin_id = None
            origin_type = None
            origin_sort_order = None
            
            # Process associations for this note item
            associations = note_item_to_associations.get(note_item.id, [])
            # print('note assoicatiosn, id', note_item.id, associations)
            
            for assoc in associations:
                a_list_id = assoc['list_id']
                assoc_list_type = assoc['list_type']
                is_origin = assoc['is_origin']
                assoc_sort_order = assoc['sort_order']
                a_page = assoc['page']
                
                # Check if this is the origin
                if is_origin:
                    origin_id = a_list_id
                    origin_type = assoc_list_type
                    origin_sort_order = assoc_sort_order
                    origin_page = a_page
                    
                # TODO: Maybe not: Potentially move checking if you are on this list here to get this list sort order
                
                # If it's a tag, add it to assigned_tags
                if assoc_list_type == 'tag' and a_list_id in tag_map:
                    tag_data.append({
                        'id': '11111111-1111-1111-1111-111111111111',
                        'name': tag_map[a_list_id]['name'],
                        'sort_order': assoc_sort_order,
                        'page': a_page
                    })
            
            note_responses.append(
                NoteResponse(
                    id=note_item.id,
                    content=note_item.content,
                    created_at=note_item.created_at,
                    updated_at=note_item.updated_at,
                    creation_list_id=origin_id,
                    creation_type=origin_type,
                    sequence_number=note_item.sequence_number,
                    tags=tag_data, #assigned_tags,
                    sort_order=sort_order,  # Include sort_order in response if needed
                    origin_sort_order= origin_sort_order,
                    origin_page=origin_page
                )
            )
        
        # Can I delete this tag ordering? The tag sort order denote's a note item's position on a list
        # Not the tag's order on a note item 
        # Create tag responses in order
        tag_responses = []
        
        # Build a map of tags by note_item_id and their sort_orders
        # tag_sort_orders isn't used even though it is set here, can I remove it
        tag_sort_orders = {}
        for a_list_id, note_item_id, b_list_type, is_origin, sort_order, a_page in tag_associations:
            if b_list_type == 'tag' and a_list_id in tag_map:
                if a_list_id not in tag_sort_orders or (sort_order is not None and (tag_sort_orders[a_list_id] is None or sort_order < tag_sort_orders[a_list_id])):
                    tag_sort_orders[a_list_id] = sort_order
        
        # Create tag responses with sort_order information
        for a_list_id, tag_info in tag_map.items():
            tag_responses.append(
                TagEntry(
                    id=a_list_id,
                    name=tag_info['name'],
                    parent_id=tag_info['parent_id'],
                    created_at=tag_info['created_at'],
                    order=tag_info['order'],
                    # This is the tag object not the assoication, the sort_order is for the note_item's position on the page
                    # not for the tag's positoin on the page. Putting none here for now, maybe alphabetical order for the future
                    sort_order=None #tag_sort_orders.get(a_list_id)  # Include sort_order if available
                )
            )
        
        # Sort tag responses by sort_order when available
        tag_responses.sort(key=lambda x: (x.sort_order is None, x.sort_order))
        
        # Sort the note items based on this list's sort_order
        note_responses.sort(key=lambda x:  (this_list_order.get(x.id) is None, this_list_order.get(x.id)))
        [print('sortOrder', this_list_order.get(x.id), 'content', x.content) for x in note_responses]
        max_page = self.get_max_page(list_id, list_type)
        return NoteItemsResponse(
            data={
                "notes": note_responses,  # Already ordered by sort_order from the query
                "tags": tag_responses,    # Ordered by sort_order
                "list_name": list_name,
                "list_type": list_type,
                "color_order": color_order,
                "max_page": max_page
            },
            message="Success",
            error=None
        )

   

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
    
    def delete_note(self, note_id: UUID, user_id:  Optional[UUID]) -> int:
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
        existing_note = self.db.query(Note).filter(
            Note.id == note_id,
            Note.created_by == user_id
        ).first()
        
        if not existing_note:
            # Return a 409 Conflict status code with a clear message
            raise HTTPException(
                status_code=404,  # Conflict is appropriate for this case
                detail=f"A note named '{note_id}' doesn't exist for this user"
            )
        
        # Delete the tag
        self.db.delete(existing_note)
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
            max_page = self.get_max_page(tag.id, 'tag')
            tag_responses.append(
                TagEntry(
                    id=tag.id,
                    name=tag.name,
                    parent_id=tag.parent_id,
                    created_at=tag.created_at,
                    order=tag.creation_order,
                    sort_order=None,
                    max_page=max_page,
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
                max_page = self.get_max_page(note.id, 'note')
                note_responses.append(
                    NoteEntry(
                        id=note.id,
                        title=note.title,
                        description=description,
                        created_at=note.created_at,
                        updated_at=note.updated_at,
                        order=i,
                        max_page=max_page,
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
