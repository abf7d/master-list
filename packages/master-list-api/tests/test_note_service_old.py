import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, update, delete, and_

# Import your models and data types
# from your_app.models import NoteItem, NoteItemList, Tag
# from your_app.schemas import CreateNoteGroup, ItemData
# from your_app.services import NoteService

class TestNoteService(unittest.TestCase):
    def setUp(self):
        # Create a mock database session
        self.db = MagicMock()
        
        # Create the service with the mock db
        self.service = NoteService(self.db)
        
        # Common test data
        self.user_id = UUID('99999999-9999-9999-9999-999999999999')
        self.parent_id = UUID('12345678-1234-5678-1234-567812345678')
        self.item1_id = UUID('11111111-1111-1111-1111-111111111111')
        self.item2_id = UUID('22222222-2222-2222-2222-222222222222')
        self.tag1_id = UUID('33333333-3333-3333-3333-333333333333')
        self.tag2_id = UUID('44444444-4444-4444-4444-444444444444')
    
    def test_categorize_items_empty(self):
        """Test categorizing an empty list of items."""
        note_group = CreateNoteGroup(
            parent_tag_id=self.parent_id,
            parent_list_type="note",
            items=[]
        )
        
        new_items, existing_items, existing_item_ids = self.service._categorize_items(
            note_group, self.parent_id, "note"
        )
        
        self.assertEqual(len(new_items), 0)
        self.assertEqual(len(existing_items), 0)
        self.assertEqual(len(existing_item_ids), 0)
    
    def test_categorize_items_only_new(self):
        """Test categorizing only new items."""
        note_group = CreateNoteGroup(
            parent_tag_id=self.parent_id,
            parent_list_type="note",
            items=[
                ItemData(
                    id=None,
                    content="New item 1",
                    tags=["tag1"],
                    creation_list_id=None,
                    creation_type=None
                ),
                ItemData(
                    id=None,
                    content="New item 2",
                    tags=["tag2"],
                    creation_list_id=None,
                    creation_type=None
                )
            ]
        )
        
        new_items, existing_items, existing_item_ids = self.service._categorize_items(
            note_group, self.parent_id, "note"
        )
        
        self.assertEqual(len(new_items), 2)
        self.assertEqual(len(existing_items), 0)
        self.assertEqual(len(existing_item_ids), 0)
        
        # Verify creation_list_id and creation_type are set for new items
        self.assertEqual(new_items[0]['data'].creation_list_id, self.parent_id)
        self.assertEqual(new_items[0]['data'].creation_type, "note")
        self.assertEqual(new_items[1]['data'].creation_list_id, self.parent_id)
        self.assertEqual(new_items[1]['data'].creation_type, "note")
    
    def test_categorize_items_mixed(self):
        """Test categorizing a mix of new and existing items."""
        note_group = CreateNoteGroup(
            parent_tag_id=self.parent_id,
            parent_list_type="note",
            items=[
                ItemData(
                    id=None,
                    content="New item",
                    tags=["tag1"],
                    creation_list_id=None,
                    creation_type=None
                ),
                ItemData(
                    id=self.item1_id,
                    content="Existing item",
                    tags=["tag2"],
                    creation_list_id=self.parent_id,
                    creation_type="note"
                )
            ]
        )
        
        new_items, existing_items, existing_item_ids = self.service._categorize_items(
            note_group, self.parent_id, "note"
        )
        
        self.assertEqual(len(new_items), 1)
        self.assertEqual(len(existing_items), 1)
        self.assertEqual(len(existing_item_ids), 1)
        self.assertEqual(existing_item_ids[0], self.item1_id)
        
        # Verify order is preserved
        self.assertEqual(new_items[0]['order'], 0)
        self.assertEqual(existing_items[0]['order'], 1)
    
    def test_get_tag_ids_map_empty(self):
        """Test getting tag IDs map with no tags."""
        note_group = CreateNoteGroup(
            parent_tag_id=self.parent_id,
            parent_list_type="note",
            items=[
                ItemData(
                    id=None,
                    content="Item with no tags",
                    tags=[],
                    creation_list_id=None,
                    creation_type=None
                )
            ]
        )
        
        tag_ids_map = self.service._get_tag_ids_map(note_group)
        
        self.assertEqual(len(tag_ids_map), 0)
        # Verify no database query was made
        self.db.execute.assert_not_called()
    
    def test_get_tag_ids_map_with_tags(self):
        """Test getting tag IDs map with tags."""
        # Set up mock database response
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (self.tag1_id, "tag1"),
            (self.tag2_id, "tag2")
        ]
        self.db.execute.return_value = mock_result
        
        note_group = CreateNoteGroup(
            parent_tag_id=self.parent_id,
            parent_list_type="note",
            items=[
                ItemData(
                    id=None,
                    content="Item 1",
                    tags=["tag1", "tag2", "tag3"],
                    creation_list_id=None,
                    creation_type=None
                ),
                ItemData(
                    id=None,
                    content="Item 2",
                    tags=["tag2", "tag4"],
                    creation_list_id=None,
                    creation_type=None
                )
            ]
        )
        
        tag_ids_map = self.service._get_tag_ids_map(note_group)
        
        # Verify the map contains the expected tag IDs
        self.assertEqual(len(tag_ids_map), 2)
        self.assertEqual(tag_ids_map["tag1"], self.tag1_id)
        self.assertEqual(tag_ids_map["tag2"], self.tag2_id)
        
        # Verify the database query was made with the correct parameters
        self.db.execute.assert_called_once()
        # Extract the query from the call arguments
        query = self.db.execute.call_args[0][0]
        self.assertIn("Tag.name.in_", str(query))
        # The query should include all unique tag names
        self.assertIn("tag1", str(query))
        self.assertIn("tag2", str(query))
        self.assertIn("tag3", str(query))
        self.assertIn("tag4", str(query))
    
    def test_update_parent_association_existing(self):
        """Test updating an existing parent association."""
        # Mock item data
        item = ItemData(
            id=self.item1_id,
            content="Test content",
            tags=["tag1"],
            creation_list_id=self.parent_id,
            creation_type="note"
        )
        
        # Mock existing associations
        existing_assoc_map = {
            (self.item1_id, self.parent_id, "note"): {
                'is_origin': True,
                'sort_order': 5
            }
        }
        
        new_associations = self.service._update_parent_association(
            item, self.item1_id, 2, self.parent_id, "note", existing_assoc_map
        )
        
        # Verify no new associations were created
        self.assertEqual(len(new_associations), 0)
        
        # Verify the update was called with correct parameters
        self.db.execute.assert_called_once()
        update_stmt = self.db.execute.call_args[0][0]
        self.assertIsInstance(update_stmt, update)
        
        # Check that sort_order is preserved
        self.assertIn("sort_order=5", str(update_stmt))
    
    def test_update_parent_association_new(self):
        """Test creating a new parent association."""
        # Mock item data
        item = ItemData(
            id=self.item1_id,
            content="Test content",
            tags=["tag1"],
            creation_list_id=self.tag1_id,  # Different from parent_id
            creation_type="tag"
        )
        
        # Empty existing associations
        existing_assoc_map = {}
        
        new_associations = self.service._update_parent_association(
            item, self.item1_id, 2, self.parent_id, "note", existing_assoc_map
        )
        
        # Verify a new association was created
        self.assertEqual(len(new_associations), 1)
        
        # Verify the new association has the correct properties
        assoc = new_associations[0]
        self.assertEqual(assoc.note_item_id, self.item1_id)
        self.assertEqual(assoc.list_id, self.parent_id)
        self.assertEqual(assoc.list_type, "note")
        self.assertEqual(assoc.is_origin, False)  # Not the origin
        self.assertEqual(assoc.sort_order, 2)
        
        # Verify the association was added to the database session
        self.db.add.assert_called_once_with(assoc)
    
    def test_update_parent_association_no_parent(self):
        """Test handling when there's no parent ID."""
        # Mock item data
        item = ItemData(
            id=self.item1_id,
            content="Test content",
            tags=["tag1"],
            creation_list_id=self.tag1_id,
            creation_type="tag"
        )
        
        # Empty existing associations
        existing_assoc_map = {}
        
        # Call with parent_id=None
        new_associations = self.service._update_parent_association(
            item, self.item1_id, 2, None, "note", existing_assoc_map
        )
        
        # Verify no associations were created
        self.assertEqual(len(new_associations), 0)
        
        # Verify no database operations were performed
        self.db.execute.assert_not_called()
        self.db.add.assert_not_called()

if __name__ == '__main__':
    unittest.main()