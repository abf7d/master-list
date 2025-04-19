from typing import List, Optional
from uuid import UUID
import uuid
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db_init.schemas import Note, Tag, NoteItem, NoteItemList
from models.models import CreateNoteGroup, NoteCreation, NoteEntry, NoteGroupResponse, NoteItemsResponse, TagEntry, TagResponse, NoteResponse
from sqlalchemy import and_, select, delete, tuple_
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
        parent_id = note_group.parent_tag_id
        parent_list_type = note_group.parent_list_type if note_group.parent_list_type is not None else origin_type
        
        # set creation id for all the new items
        for item in note_group.items:
            if item.creation_list_id == None:
                item.creation_list_id = parent_id
                item.creation_type = parent_list_type
        
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
                # and if this list is the origin, set is_origin to True
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
                tag_association = NoteItemList(
                    note_item_id=note_item.id,
                    list_id=tag_id,
                    list_type='tag',
                    is_origin=item.creation_list_id == tag_id and item.creation_type == 'tag' #(origin_type == 'tag')
                )
                self.db.add(tag_association)
                associations.append(tag_association)
            
        # for i, item in enumerate(note_group.items):
        #     # Create new note item
        #     position = item.position if item.position is not None else i
            
        #     # Use existing ID if provided, otherwise create new
        #     note_item_id = item.id if item.id else uuid.uuid4()
            
        #     # TODO: Use db to create a new id and then use that id later when creating associations
        #     # to first create the isOrigin and then the other assocaitions, need to persist origin
        #     new_note_item = NoteItem(
        #         id=note_item_id,
        #         content=item.content,
        #         created_by=user_id,
        #         sequence_number=position
        #     )
        #     self.db.add(new_note_item)
        #     created_note_items.append(new_note_item)
            
        #     # Create parent association
        #     # TODO: Need to persist the if the association is the origin and save here
        #     # Setting to False for now
        #     if parent_id:
        #         parent_association = NoteItemList(
        #             note_item_id=note_item_id,
        #             list_id=parent_id,
        #             list_type=parent_list_type,
        #             is_origin=False #(origin_type == parent_list_type)
        #         )
        #         self.db.add(parent_association)
        #         associations.append(parent_association)
            
        #     # Create tag associations
        #     # TODO: add the other tags which are not the parent tag
        #     # The data passed in includes tag name. Need to get the tag id for the tag name and update the 
        #     # associations.  
        #     # Create tag associations using tag_ids_by_name mapping
        #     for tag_name in item.tags:
        #         # Skip if tag name doesn't exist in the database
        #         if tag_name not in tag_ids_by_name:
        #             continue
                    
        #         tag_id = tag_ids_by_name[tag_name]
        #         tag_association = NoteItemList(
        #             note_item_id=note_item_id,
        #             list_id=tag_id,
        #             list_type='tag',
        #             is_origin=False #(origin_type == 'tag')
        #         )
        #         self.db.add(tag_association)
        #         associations.append(tag_association)
        
        # Commit changes
        self.db.commit()
        
        # Refresh objects to ensure they have DB-generated values
        # for note_item in created_note_items:
        #     self.db.refresh(note_item)
        
        return {
            "created_note_items": created_note_items,
            "associations": associations
        }
    
    
    
    def get_note_items(self, list_id: UUID, user_id: UUID, list_type: str = "note") -> NoteItemsResponse:#db: Session, list_id: UUID, list_type: str) -> Dict[str, Any]:
        """
        Given a list_id and list_type, retrieve all NoteItems in that list and all Tags associated with those NoteItems.
        
        Args:
            db: Database session
            list_id: UUID of the list (Note or Tag)
            list_type: Type of the list ('note' or 'tag')
            
        Returns:
            Dict containing note_items and tags
        """
        # Step 1: Get all note_item_ids for the given list_id and list_type
        note_item_ids_query = select(NoteItemList.note_item_id).where(
            and_(
                NoteItemList.list_id == list_id,
                NoteItemList.list_type == list_type
            )
        )
        note_item_ids = [row[0] for row in self.db.execute(note_item_ids_query).fetchall()]
        
        # Step 2: Get all note_items for these IDs
        note_items_query = select(NoteItem).where(
            NoteItem.id.in_(note_item_ids),
            NoteItem.created_by == user_id
        )
        note_items = self.db.execute(note_items_query).scalars().all()
        # note_items = [note_item in note_items_results]
        
        # Step 3: Get all tag associations (list_id and note_item_id pairs where list_type is 'tag')
        tag_associations_query = select(
            NoteItemList.list_id, 
            NoteItemList.note_item_id,
            NoteItemList.list_type,
            NoteItemList.is_origin
        ).where(
            and_(
                NoteItemList.note_item_id.in_(note_item_ids),
            )
        )
        tag_associations = self.db.execute(tag_associations_query).fetchall()
        
        # Extract unique tag_ids from associations
        tag_ids = list(set([association[0] for association in tag_associations if association[2] == 'tag']))
        
        # Step 4: Get all tags for these tag_ids
        tags_query = select(Tag).where(
            Tag.id.in_(tag_ids)
        )
        tags = self.db.execute(tags_query).scalars().all()
        
        # Map tag id to name for easier conversion
        tag_map = {tag.id: tag.name for tag in tags}  
       
            
        # Step 5: Construct the response    
        note_responses = []
        for note_item in note_items:
            
            assigned_tags = []
            
            origin_id = None
            origin_type = None
            for tag_id, note_item_id, list_type, is_origin in tag_associations:
                
                # if association is a tag and its note id matches this item
                if note_item_id == note_item.id and list_type == 'tag' and tag_id in tag_map:
                    name = tag_map[tag_id]
                    assigned_tags.append(name)
                if is_origin:
                    origin_id = tag_id
                    origin_type = list_type
            
            note_responses.append(
                NoteResponse(
                    id=note_item.id,
                    content=note_item.content,
                    created_at=note_item.created_at,
                    updated_at=note_item.updated_at,
                    creation_list_id=origin_id,
                    creation_type=origin_type,
                    sequence_number=note_item.sequence_number,
                    tags=assigned_tags
                )
            )
        
        
        tag_responses = [
            TagEntry(
                id=tag.id,
                name=tag.name,
                parent_id=tag.parent_id,
                created_at=tag.created_at,
                order=tag.creation_order
            )
            for tag in tags
        ]
        print(f"tag_responses: {str(tag_responses)}")
        return NoteItemsResponse(
            data={"notes": note_responses, "tags": tag_responses},
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
            order=tag.creation_order
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
                    order=tag.creation_order
                )
            )
        
        return tag_responses
    
    
    def get_notes(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        pageSize: int = 10,
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
        # if parent_tag_id is not None:
            # filters.append(Tag.parent_id == parent_tag_id)

        # Optional search query (e.g., for autocomplete)
        if query:
            filters.append(Note.title.ilike(f"{query}%"))  # Starts with; for partial match use `%{query}%`

        # Query with filters and pagination
        notes_query: Query = self.db.query(Note).filter(and_(*filters))
        
        # Need to track usage statistics: https://claude.ai/chat/5f7f1716-0dca-4db7-9d21-fcf1de0c92a6
        notes_query = notes_query.order_by(
            case((Note.title == query, 1), else_=0).desc(),
            func.length(Note.title),
            Note.created_at.desc()
        )  # Optional ordering
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