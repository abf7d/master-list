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


class UtilService:
    def __init__(self, db: Session):
        self.db = db

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
       