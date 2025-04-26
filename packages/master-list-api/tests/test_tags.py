def test_update_tag_associations_add_new(self):
    """Test adding new tag associations."""
    # Mock item data with tags
    item = ItemData(
        id=self.item1_id,
        content="Test content",
        tags=["tag1", "tag2"],
        creation_list_id=self.parent_id,
        creation_type="note"
    )
    
    # Mock tag ID mapping
    tag_ids_by_name = {
        "tag1": self.tag1_id,
        "tag2": self.tag2_id
    }
    
    # No existing associations
    existing_assoc_map = {}
    
    new_associations = self.service._update_tag_associations(
        item, self.item1_id, tag_ids_by_name, existing_assoc_map
    )
    
    # Verify two new associations were created
    self.assertEqual(len(new_associations), 2)
    
    # Verify the associations have the correct properties
    tag1_assoc = next(a for a in new_associations if a.list_id == self.tag1_id)
    self.assertEqual(tag1_assoc.note_item_id, self.item1_id)
    self.assertEqual(tag1_assoc.list_type, "tag")
    self.assertEqual(tag1_assoc.is_origin, False)
    self.assertIsNone(tag1_assoc.sort_order)
    
    tag2_assoc = next(a for a in new_associations if a.list_id == self.tag2_id)
    self.assertEqual(tag2_assoc.note_item_id, self.item1_id)
    self.assertEqual(tag2_assoc.list_type, "tag")
    self.assertEqual(tag2_assoc.is_origin, False)
    self.assertIsNone(tag2_assoc.sort_order)
    
    # Verify the associations were added to the database session
    self.assertEqual(self.db.add.call_count, 2)

def test_update_tag_associations_update_existing(self):
    """Test updating existing tag associations."""
    # Mock item data with tags
    item = ItemData(
        id=self.item1_id,
        content="Test content",
        tags=["tag1"],
        creation_list_id=self.tag1_id,  # tag1 is the origin
        creation_type="tag"
    )
    
    # Mock tag ID mapping
    tag_ids_by_name = {
        "tag1": self.tag1_id
    }
    
    # Existing association with tag1
    existing_assoc_map = {
        (self.item1_id, self.tag1_id, "tag"): {
            'is_origin': False,  # We'll update this to True
            'sort_order': 3
        }
    }
    
    new_associations = self.service._update_tag_associations(
        item, self.item1_id, tag_ids_by_name, existing_assoc_map
    )
    
    # Verify no new associations were created
    self.assertEqual(len(new_associations), 0)
    
    # Verify the update was called with correct parameters
    self.db.execute.assert_called_once()
    update_stmt = self.db.execute.call_args[0][0]
    self.assertIsInstance(update_stmt, update)
    
    # Verify is_origin was updated to True and sort_order preserved
    self.assertIn("is_origin=True", str(update_stmt))
    self.assertIn("sort_order=3", str(update_stmt))

def test_update_tag_associations_remove_old(self):
    """Test removing old tag associations."""
    # Mock item data with tags (tag2 removed)
    item = ItemData(
        id=self.item1_id,
        content="Test content",
        tags=["tag1"],  # Only tag1, tag2 is missing
        creation_list_id=self.parent_id,
        creation_type="note"
    )
    
    # Mock tag ID mapping
    tag_ids_by_name = {
        "tag1": self.tag1_id,
        "tag2": self.tag2_id
    }
    
    # Existing associations with both tag1 and tag2
    existing_assoc_map = {
        (self.item1_id, self.tag1_id, "tag"): {
            'is_origin': False,
            'sort_order': None
        },
        (self.item1_id, self.tag2_id, "tag"): {  # This should be removed
            'is_origin': False,
            'sort_order': None
        }
    }
    
    new_associations = self.service._update_tag_associations(
        item, self.item1_id, tag_ids_by_name, existing_assoc_map
    )
    
    # Verify tag2 association was deleted
    delete_calls = [call for call in self.db.execute.call_args_list 
                   if isinstance(call[0][0], delete)]
    self.assertEqual(len(delete_calls), 1)
    delete_stmt = delete_calls[0][0][0]
    self.assertIn(str(self.tag2_id), str(delete_stmt))

def test_create_new_items(self):
    """Test creating new items and their associations."""
    # Mock new items data
    new_items = [
        {
            'data': ItemData(
                id=None,
                content="New item 1",
                tags=["tag1"],
                creation_list_id=self.parent_id,
                creation_type="note",
                position=None
            ),
            'order': 0
        },
        {
            'data': ItemData(
                id=None,
                content="New item 2",
                tags=["tag1", "tag2"],
                creation_list_id=None,  # Will use parent as creation
                creation_type=None,
                position=5  # Custom position
            ),
            'order': 1
        }
    ]
    
    # Mock tag ID mapping
    tag_ids_by_name = {
        "tag1": self.tag1_id,
        "tag2": self.tag2_id
    }
    
    # Mock the created note items - simulate flush generating IDs
    created_note_item1 = MagicMock()
    created_note_item1.id = UUID('55555555-5555-5555-5555-555555555555')
    created_note_item2 = MagicMock()
    created_note_item2.id = UUID('66666666-6666-6666-6666-666666666666')
    
    # Set up the database to add these items
    def side_effect_add(obj):
        if isinstance(obj, NoteItem):
            if obj.content == "New item 1":
                obj.id = created_note_item1.id
            else:
                obj.id = created_note_item2.id
    
    self.db.add.side_effect = side_effect_add
    
    created_items, new_associations = self.service._create_new_items(
        new_items, tag_ids_by_name, self.parent_id, "note", self.user_id
    )
    
    # Verify two items were created
    self.assertEqual(len(created_items), 2)
    
    # Verify the second item uses its position value
    self.assertEqual(created_items[1].sequence_number, 5)
    
    # Verify the appropriate associations were created
    # Parent associations
    parent_assocs = [a for a in new_associations 
                    if a.list_id == self.parent_id and a.list_type == "note"]
    self.assertEqual(len(parent_assocs), 2)
    
    # Tag associations - 3 total (item1->tag1, item2->tag1, item2->tag2)
    tag_assocs = [a for a in new_associations 
                 if a.list_type == "tag"]
    self.assertEqual(len(tag_assocs), 3)
    
    # Origin associations
    origin_assocs = [a for a in new_associations if a.is_origin]
    self.assertEqual(len(origin_assocs), 2)  # Both items have origin associations
    
    # Verify the database flush was called
    self.db.flush.assert_called_once()