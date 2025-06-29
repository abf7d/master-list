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

class OverviewService:
    def __init__(self, db: Session):
        self.db = db
        self.utils = UtilService(db)
 
 
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
        max_page = self.utils.get_max_page(list_id, list_type)
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
    
    
    def delete_page(
        self,
        list_id: UUID,
        user_id: UUID,  # Not used in this method but could be useful for logging or future checks,
        list_type: str,       # 'note' or 'tag'
        page_to_delete: int
    ) -> None:
        """
        Remove a page from a note/list, delete the NoteItems on that page,
        and clean up every association that refers to those NoteItems.
        """

        if list_type not in ("note", "tag"):
            raise ValueError("list_type must be 'note' or 'tag'")

        with self.db.begin():                       # one atomic tx
        # ── 1. delete page-specific associations, grab their ids ──────────────
            item_ids_subq = (
                select(NoteItem.id)
                .join(NoteItemList, NoteItem.id == NoteItemList.note_item_id)
                .where(
                    NoteItemList.list_id   == list_id,
                    NoteItemList.list_type == list_type,
                    NoteItemList.page      == page_to_delete,
                    NoteItem.created_by    == user_id,
                )
            )

            page_assoc_cte = (
                delete(NoteItemList)
                .where(NoteItemList.note_item_id.in_(item_ids_subq))
                .returning(NoteItemList.note_item_id)
                .cte("page_assoc")
            )

            # materialise the delete
            self.db.execute(select(func.count()).select_from(page_assoc_cte))

            # ── 2. delete every remaining association for those items ─────────────
            delete_other_assoc_stmt = (
                delete(NoteItemList)
                .where(NoteItemList.note_item_id.in_(select(page_assoc_cte.c.note_item_id)))
            )
            self.db.execute(delete_other_assoc_stmt, execution_options={"synchronize_session": False})

            # ── 3. drop the NoteItem rows themselves ───────────────────────────────
            delete_items_stmt = (
                delete(NoteItem)
                .where(NoteItem.id.in_(select(page_assoc_cte.c.note_item_id)))
            )
            self.db.execute(delete_items_stmt, execution_options={"synchronize_session": False})

            # ── 4. re-number later pages ───────────────────────────────────────────
            renumber_stmt = (
                update(NoteItemList)
                .where(
                    and_(
                        NoteItemList.list_id == list_id,
                        NoteItemList.list_type == list_type,
                        NoteItemList.page > page_to_delete,
                    )
                )
                .values(page=NoteItemList.page - 1)
            )
            self.db.execute(renumber_stmt, execution_options={"synchronize_session": False})

