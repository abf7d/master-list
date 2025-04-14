from typing import List, Optional
from uuid import UUID
import uuid
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db_init.schemas import Note, Tag, NoteItem, NoteItemTag
from models.models import CreateNoteGroup, NoteGroupResponse, NoteItemsResponse, TagEntry, TagResponse, NoteResponse
from sqlalchemy import and_
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
    
        
    
    def update_note_items(self, note_group: CreateNoteGroup, user_id: UUID, origin_type: str = "tag") -> NoteGroupResponse:
        """
        Create notes under an existing tag.
        
        Args:
            tag_id: UUID of the existing parent tag
            content_list: List of text content for each note
            
        Returns:
            NoteGroupResponse with the tag and created notes
            
        Raises:
            NoResultFound: If the tag_id doesn't exist
        """
        # Verify tag/list/note exists
        origin_list = None
        if (origin_type == "note"):
            origin_list = self.db.query(Note).filter(Note.id == note_group.parent_tag_id, Tag.created_by == user_id).first()
        else:
            origin_list = self.db.query(Tag).filter(Tag.id == note_group.parent_tag_id, Tag.created_by == user_id).first()
        if not origin_list:
            raise NoResultFound(f"Tag with id {note_group.parent_tag_id} by {user_id} not found")
        
        # delete all of the notes with the parent_tag_id
        # TODO: !!!!!!!!Need to add NoteItem.origin_type == 'notes'
        # TODO: !!!!!!!!also need to add 'tag' or 'note' to origin_type when creating the note
        # need to get all of the notes for the specified tag and then delete all of the NoteItemTags assocatiated with those notes
        
        # self.db.query(NoteItemTag).filter(NoteItemTag. == note_group.parent_tag_id).delete()
        # self.db.commit()
        
        # Have to delete the noteTags that were set on this page but are not the parent note, need to add a field to the note tag origin_tag_id
        
        #Need to get the tag ids for all of the notes that have origin_id == note_group.parent_tag_id and delete the associated note_tags
        note_items = self.db.query(NoteItem).filter(NoteItem.origin_id == note_group.parent_tag_id, NoteItemTag.origin_type == origin_type)
        self.db.query(NoteItemTag).filter(NoteItemTag.note_item_id.in_([note.id for note in note_items])).delete()
        
        # Delete all of the NoteTag associations for the parent tag
        # self.db.query(NoteItemTag).filter(NoteItemTag.tag_id == note_group.parent_tag_id, NoteItemTag.origin_type == origin_type, NoteItemTag.tag_id == note_group.parent_tag_id).delete() # NoteTag.note_id.in_([note.id for note in notes])).delete()
        self.db.query(NoteItemTag).filter(NoteItemTag.tag_id == note_group.parent_tag_id).delete() # NoteTag.note_id.in_([note.id for note in notes])).delete()
        
        # Need to add NoteItem.origin_type == 'notes'
        self.db.query(NoteItem).filter(NoteItem.origin_id == note_group.parent_tag_id, NoteItem.created_by == user_id).delete()
        self.db.commit()
        
        # Create notes
        notes = []
        for i, item in enumerate(note_group.items):
            
            # Note table has user_id as foreign key
            # but we need oauth_id because that is what
            # we are using for the user_id here
            note = NoteItem(
                id=item.id,
                content=item.content,
                origin_id=note_group.parent_tag_id,
                origin_type=origin_type,
                sequence_number=item.position,
                created_by=user_id
            )
            self.db.add(note)
            notes.append(note)
        
        self.db.flush()
        
        
        
        # Create note-tag associations
        for note, item in zip(notes, note_group.items):
            note_item_tag = NoteItemTag(
                note_item_id=note.id,
                tag_id=note_group.parent_tag_id,
                origin_type=origin_type,
                # origin_id=note_group.parent_tag_id
            )
            self.db.add(note_item_tag)
            
            # assign tags to the note, need to not duplicate tags
            print(f"item.id: {item.id}")
            print(f"item.tags: {item.tags}")
            for tag_name in item.tags:
                
                #get the tag id first
                tag_obj = self.db.query(Tag).filter(Tag.name == tag_name, Tag.created_by == user_id).first()
                if not tag_obj:
                    raise NoResultFound(f"Tag with name {tag_name} by {user_id} not found")
                
                # create NoteTag if it doesn't exist
                existing_note_tag = self.db.query(NoteItemTag).filter(
                    NoteItemTag.note_item_id == note.id,
                    NoteItemTag.tag_id == tag_obj.id,
                    NoteItemTag.origin_type == 'tag',
                ).first()
                if not existing_note_tag:
                    # Create a new NoteTag association
                    note_item_tag = NoteItemTag(
                        note_item_id=note.id,
                        tag_id=tag_obj.id,
                        origin_type='tag',
                    )
                    self.db.add(note_item_tag)
                
               
        
        # Commit changes
        self.db.commit()
        
        # Refresh objects from DB to get all fields
        for note in notes:
            self.db.refresh(note)
        
        # Construct response
        # tag_response = TagResponse(
        #     id=tag.id,
        #     name=tag.name,
        #     parent_id=tag.parent_id,
        #     created_at=tag.created_at
        # )
        
        # note_responses = []
        # for note in notes:
        #     note_responses.append(
        #         NoteResponse(
        #             id=note.id,
        #             content=note.content,
        #             created_at=note.created_at,
        #             updated_at=note.updated_at,
        #             creation_tag_id=note.creation_tag_id,
        #             sequence_number=note.sequence_number,
        #             tags=[tag_response]  # Each note has the parent tag
        #         )
        #     )
        
        # return NoteGroupResponse(
        #     tag=tag_response,
        #     notes=note_responses
        # )
        
        return NoteItemsResponse(
            message="Success",
            error=None,
            data='test1234'
        )
    
    def get_note_items(self, parent_tag_id: UUID, user_id: UUID, origin_type: str = "tag") -> NoteItemsResponse:
        """
        Get notes under an existing tag.
        
        Args:
            tag_id: UUID of the existing parent tag
            
        Returns:
            NoteGroupResponse with the tag and created notes
            
        Raises:
            NoResultFound: If the tag_id doesn't exist
        """
        # TODO: verity note exists
        # Verify tag exists
        tag = self.db.query(Tag).filter(Tag.id == parent_tag_id, Tag.created_by == user_id).first()
        if not tag:
            raise NoResultFound(f"Tag with id {parent_tag_id} by {user_id} not found")
        
        # TODO: use origin type to get the notes
        # Get notes
        note_items = self.db.query(NoteItem).filter(NoteItem.origin_id == parent_tag_id, NoteItem.origin_type == origin_type, NoteItem.created_by == user_id).order_by(NoteItem.sequence_number).all()
        
        # Get all note_tags for the notes where tag_id is not the parent tag
        note_item_tags = self.db.query(NoteItemTag).filter(
            NoteItemTag.note_item_id.in_([note_item.id for note_item in note_items]),
            NoteItemTag.tag_id != parent_tag_id
        ).all()
        
        note_item_tag_ids = [note_item_tag.tag_id for note_item_tag in note_item_tags]
        # print all of the note_tags and properties
        # print(f"note_tags: {str(note_item_tag_ids)}")
        
        # Get all tags for the notes
        tags = self.db.query(Tag).filter(
            Tag.id.in_(note_item_tag_ids),
            # Tag.parent_id != parent_tag_id
        ).all()

        print(f"tags: {str(tags)}")
        # Create a mapping of tag_id to Tag object for quick lookup
        tag_map = {tag.id: tag for tag in tags}

        # Construct response
        note_responses = []
        for note_item in note_items:
            # Get the tags for the note
            assigned_tags = []
            
            for note_tag in note_item_tags:
                if note_tag.note_item_id == note_item.id and note_tag.tag_id in tag_map:
                    tag = tag_map[note_tag.tag_id]
                    assigned_tags.append(tag.name)
            print(f"assigned_tags: {str(assigned_tags)}")
            note_responses.append(
                NoteResponse(
                    id=note_item.id,
                    content=note_item.content,
                    created_at=note_item.created_at,
                    updated_at=note_item.updated_at,
                    creation_tag_id=note_item.origin_id,
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
        
    # def get_note_itemsJOINS(self, parent_tag_id: UUID, user_id: UUID, origin_type: str = "tag") -> NoteItemsResponse:
    #     """
    #     Get notes under an existing tag.
        
    #     Args:
    #         parent_tag_id: UUID of the existing parent tag
    #         user_id: UUID of the user
    #         origin_type: Origin type ("tag" or "note")
            
    #     Returns:
    #         NoteItemsResponse with the tag and created notes
            
    #     Raises:
    #         NoResultFound: If the tag_id doesn't exist
    #     """
    #     # Verify tag exists in a single query
    #     tag = self.db.query(Tag).filter(Tag.id == parent_tag_id, Tag.created_by == user_id).first()
    #     if not tag:
    #         raise NoResultFound(f"Tag with id {parent_tag_id} by {user_id} not found")
        
    #     # Use a join to get note items and their tags in a single query
    #     query = (
    #         self.db.query(
    #             NoteItem,
    #             Tag
    #         )
    #         .outerjoin(
    #             NoteItemTag, 
    #             and_(
    #                 NoteItemTag.note_item_id == NoteItem.id,
    #                 NoteItemTag.tag_id != parent_tag_id
    #             )
    #         )
    #         .outerjoin(
    #             Tag, 
    #             Tag.id == NoteItemTag.tag_id
    #         )
    #         .filter(
    #             NoteItem.origin_id == parent_tag_id,
    #             NoteItem.origin_type == origin_type,
    #             NoteItem.created_by == user_id
    #         )
    #         .order_by(NoteItem.sequence_number)
    #     )
        
    #     # Process the results
    #     note_items_dict = {}
    #     tags_dict = {}
        
    #     for note_item, tag in query:
    #         # Initialize note item entry if not already present
    #         if note_item.id not in note_items_dict:
    #             note_items_dict[note_item.id] = {
    #                 "note_item": note_item,
    #                 "tags": []
    #             }
            
    #         # Add tag to note item if it exists
    #         if tag and tag.id not in [t.id for t in note_items_dict[note_item.id]["tags"]]:
    #             note_items_dict[note_item.id]["tags"].append(tag)
    #             tags_dict[tag.id] = tag
        
    #     # Construct response
    #     note_responses = []
    #     for note_data in note_items_dict.values():
    #         note_item = note_data["note_item"]
    #         assigned_tags = [tag.name for tag in note_data["tags"] if tag]
            
    #         note_responses.append(
    #             NoteResponse(
    #                 id=note_item.id,
    #                 content=note_item.content,
    #                 created_at=note_item.created_at,
    #                 updated_at=note_item.updated_at,
    #                 creation_tag_id=note_item.origin_id,
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
    #         for tag in tags_dict.values()
    #     ]
        
    #     return NoteItemsResponse(
    #         data={"notes": note_responses, "tags": tag_responses},
    #         message="Success",
    #         error=None
    #     )

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
                    creation_tag_id=note.creation_tag_id,
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