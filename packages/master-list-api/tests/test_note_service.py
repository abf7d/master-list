# test_note_service.py
import pytest
import uuid
from datetime import datetime
from sqlalchemy import select

from models.models import CreateNoteGroup, NoteItem
from db_init.schemas import NoteItemList

# pytest -xvs tests/test_note_service.py

def test_categorize_items(note_service, test_note): #test_user
    """Test categorizing items."""
    parent_id = test_note.id
    print('start')
    note_group = CreateNoteGroup(
        parent_tag_id=parent_id,
        parent_list_type="note",
        items=[
            NoteItem(
                id=None,
                content="New item",
                tags=["tag1"],
                creation_list_id=None,
                creation_type=None
            ),
            NoteItem(
                id=uuid.uuid4(),
                content="Existing item",
                tags=["tag2"],
                creation_list_id=parent_id,
                creation_type="note"
            )
        ]
    )
    print('notegroup', note_group)
    new_items, existing_items, existing_item_ids = note_service._categorize_items(
        note_group, parent_id, "note"
    )
    
    assert len(new_items) == 1
    assert len(existing_items) == 1
    assert len(existing_item_ids) == 1
    
    # Verify creation_list_id is set for new item
    assert new_items[0]['data'].creation_list_id == parent_id
    assert new_items[0]['data'].creation_type == "note"

def test_get_tag_ids_map(note_service, test_tags):
    """Test getting tag IDs map."""
    note_group = CreateNoteGroup(
        parent_tag_id=None,
        parent_list_type=None,
        items=[
            NoteItem(
                id=None,
                content="Item with tags",
                tags=["tag1", "tag2", "tag3"],
                creation_list_id=None,
                creation_type=None
            )
        ]
    )
    
    tag_ids_map = note_service._get_tag_ids_map(note_group)
    
    # Should find the two tags we created in the fixture
    assert len(tag_ids_map) == 2
    assert "tag1" in tag_ids_map
    assert "tag2" in tag_ids_map
    assert tag_ids_map["tag1"] == test_tags[0].id
    assert tag_ids_map["tag2"] == test_tags[1].id

def test_update_parent_association_new(note_service, test_user, test_note, test_tags):
    """Test creating a new parent association."""
    # Item data with a different origin
    item = NoteItem(
        id=uuid.uuid4(),
        content="Test content",
        tags=["tag1"],
        creation_list_id=test_tags[0].id,  # Origin is tag1
        creation_type="tag"
    )
    
    # No existing associations
    existing_assoc_map = {}
    
    # Should create a new association to the note
    new_associations = note_service._update_parent_association(
        item, item.id, 3, test_note.id, "note", existing_assoc_map
    )
    
    assert len(new_associations) == 1
    assoc = new_associations[0]
    assert assoc.note_item_id == item.id
    assert assoc.list_id == test_note.id
    assert assoc.list_type == "note"
    assert assoc.is_origin == False  # Not the origin
    assert assoc.sort_order == 3

# def test_update_existing_items(note_service, test_user, test_note, test_tags, test_note_items):
#     """Test updating existing items."""
#     # Get existing associations for test_note_items[0]
#     existing_assoc_query = select(
#         NoteItemList.list_id,
#         NoteItemList.note_item_id,
#         NoteItemList.list_type,
#         NoteItemList.is_origin,
#         NoteItemList.sort_order
#     ).where(NoteItemList.note_item_id == test_note_items[0].id)
    
#     existing_associations = note_service.db.execute(existing_assoc_query).fetchall()
#     existing_assoc_map = {}
    
#     for list_id, note_item_id, list_type, is_origin, sort_order in existing_associations:
#         key = (note_item_id, list_id, list_type)
#         existing_assoc_map[key] = {
#             'is_origin': is_origin,
#             'sort_order': sort_order
#         }
    
#     # Update the item
#     existing_items = [
#         {
#             'data': NoteItem(
#                 id=test_note_items[0].id,
#                 content="Updated content",
#                 tags=["tag1", "tag2"],  # Add tag2
#                 creation_list_id=test_note.id,
#                 creation_type="note",
#                 position=None
#             ),
#             'order': 0
#         }
#     ]
    
#     tag_ids_by_name = {
#         "tag1": test_tags[0].id,
#         "tag2": test_tags[1].id
#     }
    
#     updated_items, new_associations = note_service._update_existing_items(
#         existing_items, existing_assoc_map, tag_ids_by_name, test_note.id, "note"
#     )
    
#     # Verify the item was updated
#     assert len(updated_items) == 1
#     assert updated_items[0].content == "Updated content"
    
#     # Should create one new association (to tag2)
#     assert len(new_associations) == 1
#     assert new_associations[0].list_id == test_tags[1].id
#     assert new_associations[0].note_item_id == test_note_items[0].id
#     assert new_associations[0].list_type == "tag"

# def test_create_new_items(note_service, test_user, test_note, test_tags):
#     """Test creating new items."""
#     new_items = [
#         {
#             'data': NoteItem(
#                 id=None,
#                 content="Brand new item",
#                 tags=["tag1", "tag2"],
#                 creation_list_id=test_note.id,
#                 creation_type="note",
#                 position=None
#             ),
#             'order': 0
#         }
#     ]
    
#     tag_ids_by_name = {
#         "tag1": test_tags[0].id,
#         "tag2": test_tags[1].id
#     }
    
#     created_items, new_associations = note_service._create_new_items(
#         new_items, tag_ids_by_name, test_note.id, "note", test_user.oauth_id
#     )
    
#     # Verify the item was created
#     assert len(created_items) == 1
#     assert created_items[0].content == "Brand new item"
    
#     # Should create 3 associations:
#     # 1. To the parent note (with is_origin=True)
#     # 2. To tag1
#     # 3. To tag2
#     assert len(new_associations) == 3

def test_update_items_integration(note_service, test_user, test_note, test_tags, test_note_items):
    """Integration test for the update_items function."""
    # Create a note group with one existing item and one new item
    

    print('!!!!!!!!!! 123 4')
    
    note_group = CreateNoteGroup(
        parent_tag_id=test_note.id,
        parent_list_type="note",
        items=[
            # Update existing item
            NoteItem(
                id=test_note_items[0].id,
                content="Updated content",
                tags=["tag1", "tag2"],  # Add a new tag
                creation_list_id=test_note.id,
                creation_type="note",
                position=10  # Change position
            ),
            # Create new item
            NoteItem(
                id=None,
                content="Brand new item",
                tags=["tag2"],
                creation_list_id=None,
                creation_type=None,
                position=None
            )
        ]
    )
    
    result = note_service.update_items(note_group, test_user.oauth_id)
    
    # Verify the result
    assert "created_note_items" in result
    assert "associations" in result
    assert len(result["created_note_items"]) == 2  # 1 updated + 1 new
    
    # Check that the existing item was updated
    updated_item = next(item for item in result["created_note_items"] 
                       if item.id == test_note_items[0].id)
    assert updated_item.content == "Updated content"
    assert updated_item.sequence_number == 10
    
    # Check that a new item was created
    new_item = next(item for item in result["created_note_items"] 
                   if item.id != test_note_items[0].id)
    assert new_item.content == "Brand new item"
    
    # Get the associations for the updated item to verify tags
    assoc_query = select(
        NoteItemList.list_id,
        NoteItemList.list_type
    ).where(NoteItemList.note_item_id == test_note_items[0].id)
    
    associations = note_service.db.execute(assoc_query).fetchall()
    tag_assocs = [list_id for list_id, list_type in associations if list_type == "tag"]
    
    # Should have associations to both tags
    assert len(tag_assocs) == 2
    assert test_tags[0].id in tag_assocs
    assert test_tags[1].id in tag_assocs