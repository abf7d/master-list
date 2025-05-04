# test_note_service.py
from typing import List
import pytest
import uuid
from datetime import datetime
from sqlalchemy import select

from models.models import CreateNoteGroup, NoteItem, TagProps, NoteItemsResponse, NoteResponse
from db_init.schemas import NoteItemList, Tag

# pytest -xvs tests/test_note_service.py

# def test_categorize_items(note_service, test_note): #test_user
#     """Test categorizing items."""
#     parent_id = test_note.id
#     print('start')
#     note_group = CreateNoteGroup(
#         parent_tag_id=parent_id,
#         parent_list_type="note",
#         items=[
#             NoteItem(
#                 id=None,
#                 content="New item",
#                 tags=["tag1"],
#                 creation_list_id=None,
#                 creation_type=None
#             ),
#             NoteItem(
#                 id=uuid.uuid4(),
#                 content="Existing item",
#                 tags=["tag2"],
#                 creation_list_id=parent_id,
#                 creation_type="note"
#             )
#         ]
#     )
#     print('notegroup', note_group)
#     new_items, existing_items, existing_item_ids = note_service._categorize_items(
#         note_group, parent_id, "note"
#     )
    
#     assert len(new_items) == 1
#     assert len(existing_items) == 1
#     assert len(existing_item_ids) == 1
    
#     # Verify creation_list_id is set for new item
#     assert new_items[0]['data'].creation_list_id == parent_id
#     assert new_items[0]['data'].creation_type == "note"

# def test_get_tag_ids_map(note_service, test_tags):
#     """Test getting tag IDs map."""
#     note_group = CreateNoteGroup(
#         parent_tag_id=None,
#         parent_list_type=None,
#         items=[
#             NoteItem(
#                 id=None,
#                 content="Item with tags",
#                 tags=["tag1", "tag2", "tag3"],
#                 creation_list_id=None,
#                 creation_type=None
#             )
#         ]
#     )
    
#     tag_ids_map = note_service._get_tag_ids_map(note_group)
    
#     # Should find the two tags we created in the fixture
#     assert len(tag_ids_map) == 2
#     assert "tag1" in tag_ids_map
#     assert "tag2" in tag_ids_map
#     assert tag_ids_map["tag1"] == test_tags[0].id
#     assert tag_ids_map["tag2"] == test_tags[1].id

# def test_update_parent_association_new(note_service, test_user, test_note, test_tags):
#     """Test creating a new parent association."""
#     # Item data with a different origin
#     item = NoteItem(
#         id=uuid.uuid4(),
#         content="Test content",
#         tags=["tag1"],
#         creation_list_id=test_tags[0].id,  # Origin is tag1
#         creation_type="tag"
#     )
    
#     # No existing associations
#     existing_assoc_map = {}
    
#     # Should create a new association to the note
#     new_associations = note_service._update_parent_association(
#         item, item.id, 3, test_note.id, "note", existing_assoc_map
#     )
    
#     assert len(new_associations) == 1
#     assoc = new_associations[0]
#     assert assoc.note_item_id == item.id
#     assert assoc.list_id == test_note.id
#     assert assoc.list_type == "note"
#     assert assoc.is_origin == False  # Not the origin
#     assert assoc.sort_order == 3

# # def test_update_existing_items(note_service, test_user, test_note, test_tags, test_note_items):
# #     """Test updating existing items."""
# #     # Get existing associations for test_note_items[0]
# #     existing_assoc_query = select(
# #         NoteItemList.list_id,
# #         NoteItemList.note_item_id,
# #         NoteItemList.list_type,
# #         NoteItemList.is_origin,
# #         NoteItemList.sort_order
# #     ).where(NoteItemList.note_item_id == test_note_items[0].id)
    
# #     existing_associations = note_service.db.execute(existing_assoc_query).fetchall()
# #     existing_assoc_map = {}
    
# #     for list_id, note_item_id, list_type, is_origin, sort_order in existing_associations:
# #         key = (note_item_id, list_id, list_type)
# #         existing_assoc_map[key] = {
# #             'is_origin': is_origin,
# #             'sort_order': sort_order
# #         }
    
# #     # Update the item
# #     existing_items = [
# #         {
# #             'data': NoteItem(
# #                 id=test_note_items[0].id,
# #                 content="Updated content",
# #                 tags=["tag1", "tag2"],  # Add tag2
# #                 creation_list_id=test_note.id,
# #                 creation_type="note",
# #                 position=None
# #             ),
# #             'order': 0
# #         }
# #     ]
    
# #     tag_ids_by_name = {
# #         "tag1": test_tags[0].id,
# #         "tag2": test_tags[1].id
# #     }
    
# #     updated_items, new_associations = note_service._update_existing_items(
# #         existing_items, existing_assoc_map, tag_ids_by_name, test_note.id, "note"
# #     )
    
# #     # Verify the item was updated
# #     assert len(updated_items) == 1
# #     assert updated_items[0].content == "Updated content"
    
# #     # Should create one new association (to tag2)
# #     assert len(new_associations) == 1
# #     assert new_associations[0].list_id == test_tags[1].id
# #     assert new_associations[0].note_item_id == test_note_items[0].id
# #     assert new_associations[0].list_type == "tag"

# # def test_create_new_items(note_service, test_user, test_note, test_tags):
# #     """Test creating new items."""
# #     new_items = [
# #         {
# #             'data': NoteItem(
# #                 id=None,
# #                 content="Brand new item",
# #                 tags=["tag1", "tag2"],
# #                 creation_list_id=test_note.id,
# #                 creation_type="note",
# #                 position=None
# #             ),
# #             'order': 0
# #         }
# #     ]
    
# #     tag_ids_by_name = {
# #         "tag1": test_tags[0].id,
# #         "tag2": test_tags[1].id
# #     }
    
# #     created_items, new_associations = note_service._create_new_items(
# #         new_items, tag_ids_by_name, test_note.id, "note", test_user.oauth_id
# #     )
    
# #     # Verify the item was created
# #     assert len(created_items) == 1
# #     assert created_items[0].content == "Brand new item"
    
# #     # Should create 3 associations:
# #     # 1. To the parent note (with is_origin=True)
# #     # 2. To tag1
# #     # 3. To tag2
# #     assert len(new_associations) == 3

# def test_update_items_integration(note_service, test_user, test_note, test_tags, test_note_items):
#     """Integration test for the update_items function."""
#     # Create a note group with one existing item and one new item
    

#     print('!!!!!!!!!! 123 4')
    
#     note_group = CreateNoteGroup(
#         parent_tag_id=test_note.id,
#         parent_list_type="note",
#         items=[
#             # Update existing item
#             NoteItem(
#                 id=test_note_items[0].id,
#                 content="Updated content",
#                 tags=["tag1", "tag2"],  # Add a new tag
#                 creation_list_id=test_note.id,
#                 creation_type="note",
#                 position=10  # Change position
#             ),
#             # Create new item
#             NoteItem(
#                 id=None,
#                 content="Brand new item",
#                 tags=["tag2"],
#                 creation_list_id=None,
#                 creation_type=None,
#                 position=None
#             )
#         ]
#     )
    
#     result = note_service.update_items(note_group, test_user.oauth_id)
    
#     # Verify the result
#     assert "created_note_items" in result
#     assert "associations" in result
#     assert len(result["created_note_items"]) == 2  # 1 updated + 1 new
    
#     # Check that the existing item was updated
#     updated_item = next(item for item in result["created_note_items"] 
#                        if item.id == test_note_items[0].id)
#     assert updated_item.content == "Updated content"
#     # assert updated_item.sequence_number == 10
    
#     # Check that a new item was created
#     new_item = next(item for item in result["created_note_items"] 
#                    if item.id != test_note_items[0].id)
#     assert new_item.content == "Brand new item"
    
#     # Get the associations for the updated item to verify tags
#     assoc_query = select(
#         NoteItemList.list_id,
#         NoteItemList.list_type
#     ).where(NoteItemList.note_item_id == test_note_items[0].id)
    
#     associations = note_service.db.execute(assoc_query).fetchall()
#     tag_assocs = [list_id for list_id, list_type in associations if list_type == "tag"]
    
#     # Should have associations to both tags
#     assert len(tag_assocs) == 2
#     assert test_tags[0].id in tag_assocs
#     assert test_tags[1].id in tag_assocs
    

    
def get_test_create_group(test_note) :
    return CreateNoteGroup(
        parent_tag_id=test_note.id,
        parent_list_type="note",
        items=[
            # Update existing item
            NoteItem(
                id=None,
                content="New item 1",
                tags=[
                    TagProps(
                        name="tag1",
                        sort_order=6, 
                        id=None
                    )],  # Add a new tag
                creation_list_id=None,
                # creation_type="note",
                position=None  # Change position
            ),
            # Create new item
            NoteItem(
                id=None,
                content="Brand new item 2",
                tags=[
                    TagProps(
                        name="tag1",
                        sort_order=5, 
                        id=None
                    ),
                    TagProps(
                        name="tag2",
                        sort_order=2, 
                        id=None
                    )
                ],
                creation_list_id=None,
                # creation_type="note",
                position=None
            ),
            NoteItem(
                id=None,
                content="new item 3",
                tags=[
                    TagProps(
                    name="tag2",
                    sort_order=4, 
                    id=None
                )],
                creation_list_id=None,
                # creation_type="note",
                position=None
            )
        ]
    )
    
def test_create_single_note(note_service, test_user, test_tags, test_note):
    note_group = get_test_create_group(test_note)
    note_service.update_note_items_sort_order(note_group, test_user.oauth_id, "note")
    note_service.update_note_items_sort_order(note_group, test_user.oauth_id, "note")
    response = note_service.get_note_items(test_note.id, test_user.oauth_id, "note")
    responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
    responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
    
    assert len(response.data['notes']) == 3
    assert len(responseT1.data['notes']) == 2
    assert len(responseT2.data['notes']) == 2
    
    # assert the original note is in order
    assert response.data['notes'][0].content == "New item 1"
    assert response.data['notes'][1].content == "Brand new item 2"
    assert response.data['notes'][2].content == "new item 3"
    
    # assert that the first tag list returned with referesed items due to the sort order
    assert responseT1.data['notes'][0].content == "Brand new item 2"
    assert responseT1.data['notes'][1].content == "New item 1"
    
    # assert that the second tag list returned with the items ordered correctly
    assert responseT2.data['notes'][0].content == "Brand new item 2"
    assert responseT2.data['notes'][1].content == "new item 3"
    
    # origin_sort_order for these in the first tag list is reversed because of the tag sort order
    # also check the expected sort order (the second item has 2 tags that aren't returning in the right order right now)
    assert responseT1.data['notes'][0].origin_sort_order == 1
    assert responseT1.data['notes'][1].origin_sort_order == 0
    assert responseT1.data['notes'][1].tags[0].name == "tag1"
    assert responseT1.data['notes'][1].tags[0].sort_order == 6
    
    # asert that the first tag of the second note has the right sort order
    # the first note item has two tags the order of which is not being returned correctly
    assert responseT2.data['notes'][1].tags[0].name == "tag2"
    assert responseT2.data['notes'][1].tags[0].sort_order == 4
    
    assoc_query = select(
        NoteItemList.note_item_id,
        NoteItemList.list_id,
        NoteItemList.sort_order,
        NoteItemList.list_type,
        NoteItemList.is_origin
    ).where(NoteItemList.list_type=="note")
    
    associations = note_service.db.execute(assoc_query).fetchall()
    print('1) !!!!!!!!! associations', associations)
    
    
    
    # # modify content for top note items in two tags, 
    # requestT1: CreateNoteGroup = convert_response_to_request(responseT1, test_tags[0].id, 'tag')
    # requestT1.items[0].content = "Changed 1!!"
    # note_service.update_note_items_sort_order(requestT1, test_user.oauth_id, "tag")
    
    requestT2: CreateNoteGroup = convert_response_to_request(responseT2, test_tags[1].id, 'tag')
    requestT2.items[0].content = "Changed 2!!"
    note_service.update_note_items_sort_order(requestT2, test_user.oauth_id, "tag")
    
    
    responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
    assert responseT1.data['notes'][0].content == "Changed 2!!"
    
    # assoc_query = select(
    #     NoteItemList.note_item_id,
    #     NoteItemList.list_id,
    #     NoteItemList.sort_order,
    #     NoteItemList.list_type,
    #     NoteItemList.is_origin
    # ).where(NoteItemList.list_type=="note")
    
    # associations = note_service.db.execute(assoc_query).fetchall()
    # print('!!!!!!!!! associations', associations)
    
    # # Check if same number of items 
    # response = note_service.get_note_items(test_note.id, test_user.oauth_id, "note")
    # responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
    # responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
    # assert len(response.data['notes']) == 3
    # assert len(responseT1.data['notes']) == 2
    # assert len(responseT2.data['notes']) == 2
    
    
    
    
    
    # # intermitent save to reflect note open in ui
    # response = intermitent_save(response, test_note.id, "note", test_user, note_service)
    # responseT1 = intermitent_save(responseT1, test_tags[0].id, "tag", test_user, note_service)
    # responseT2 = intermitent_save(responseT2, test_tags[1].id, "tag", test_user, note_service)
    # assert len(responseT1.data['notes']) == 2
    # assert len(responseT2.data['notes']) == 2
    
    # print('response after changes and intermitent save', response)
    
    # # Check if main note reflects both changes
    # assert response.data['notes'][0].content == "Changed 1!!"
    # assert response.data['notes'][1].content == "Changed 2!!"
    
    # # Get individual tags to see if top notes contain changed text
    # responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
    # responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
    
    # assert responseT1.data['notes'][0].content == "Changed 1!!"
    # assert responseT2.data['notes'][0].content == "Changed 2!!"
    
    
    
    
    
# This uses the old update_note_items because the new way is producing duplcate, all test above are void
# def test_update_items_multiple_saves_integration(note_service, test_user, test_tags, test_note):
#     """Integration test for the update_items function."""
#     # Create a note group with one existing item and one new item
    

#     print('!!!!!!!!!! 123 4')
    
#     note_group = CreateNoteGroup(
#         parent_tag_id=test_note.id,
#         parent_list_type="note",
#         items=[
#             # Update existing item
#             NoteItem(
#                 id=None,
#                 content="New item 1",
#                 tags=[
#                     TagProps(
#                         name="tag1",
#                         sort_order=6, 
#                         id=None
#                     )],  # Add a new tag
#                 creation_list_id=None,
#                 # creation_type="note",
#                 position=None  # Change position
#             ),
#             # Create new item
#             NoteItem(
#                 id=None,
#                 content="Brand new item 2",
#                 tags=[
#                     TagProps(
#                         name="tag1",
#                         sort_order=5, 
#                         id=None
#                     ),
#                     TagProps(
#                         name="tag2",
#                         sort_order=2, 
#                         id=None
#                     )
#                 ],
#                 creation_list_id=None,
#                 # creation_type="note",
#                 position=None
#             ),
#             NoteItem(
#                 id=None,
#                 content="new item 3",
#                 tags=[
#                     TagProps(
#                     name="tag2",
#                     sort_order=4, 
#                     id=None
#                 )],
#                 creation_list_id=None,
#                 # creation_type="note",
#                 position=None
#             )
#         ]
#     )
    
#     # Save the items, get then and then use the ids to look up in the database
#     # This uses the old update_note_items because the new way is producing duplcate, all test above are void
#     note_service.update_note_items_sort_order(note_group, test_user.oauth_id, "note")
#     note_service.update_note_items_sort_order(note_group, test_user.oauth_id, "note")
#     response = note_service.get_note_items(test_note.id, test_user.oauth_id, "note")
#     responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
#     responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
#     # assert that order for tag1 is  Brand new item 2, New item 1
#     # assert that order for tag2 is Brand new item 2, new item 3
#     # see if you can get the sort order of the note items which should be 5,6 for tag1 or tag[0] and 2,4 for tag2 or tag[1]
#     # print('response', response)
    
#     # tag_ids = [tag.id for tag in response.tags]
#     assoc_query = select(
#         NoteItemList.note_item_id,
#         NoteItemList.list_id,
#         NoteItemList.sort_order,
#     ).where(NoteItemList.list_type=="note")
    
#     # associations = note_service.db.execute(assoc_query).fetchall()
#     # print('associations', associations)
    
#     assert len(response.data['notes']) == 3
#     assert len(responseT1.data['notes']) == 2
#     assert len(responseT2.data['notes']) == 2
    
#     # modify content for top note items in two tags, 
#     requestT1: CreateNoteGroup = convert_response_to_request(responseT1, test_tags[0].id, 'tag')
#     requestT1.items[0].content = "Changed 1!!"
#     note_service.update_note_items_sort_order(requestT1, test_user.oauth_id, "tag")
    
#     requestT2: CreateNoteGroup = convert_response_to_request(responseT2, test_tags[1].id, 'tag')
#     requestT2.items[0].content = "Changed 2!!"
#     note_service.update_note_items_sort_order(requestT2, test_user.oauth_id, "tag")
    
#     # Check if same number of items 
#     response = note_service.get_note_items(test_note.id, test_user.oauth_id, "note")
#     responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
#     responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
#     assert len(response.data['notes']) == 3
#     assert len(responseT1.data['notes']) == 2
#     assert len(responseT2.data['notes']) == 2
    
#     # intermitent save to reflect note open in ui
#     response = intermitent_save(response, test_note.id, "note", test_user, note_service)
#     responseT1 = intermitent_save(responseT1, test_tags[0].id, "tag", test_user, note_service)
#     responseT2 = intermitent_save(responseT2, test_tags[1].id, "tag", test_user, note_service)
#     assert len(responseT1.data['notes']) == 2
#     assert len(responseT2.data['notes']) == 2
    
#     print('response after changes and intermitent save', response)
    
#     # Check if main note reflects both changes
#     assert response.data['notes'][0].content == "Changed 1!!"
#     assert response.data['notes'][1].content == "Changed 2!!"
    
#     # Get individual tags to see if top notes contain changed text
#     responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
#     responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
    
#     assert responseT1.data['notes'][0].content == "Changed 1!!"
#     assert responseT2.data['notes'][0].content == "Changed 2!!"
    
    
#     # change items in main note and check they reflect in the tags
#     response = note_service.get_note_items(test_note.id, test_user.oauth_id, "note")
#     request: CreateNoteGroup = convert_response_to_request(response, test_note.id, 'note')
#     request.items[0].content = "Changed 3!!"
#     request.items[1].content = "Changed 4!!"
#     note_service.update_note_items_sort_order(request, test_user.oauth_id, "note")
#     responseT1 = note_service.get_note_items(test_tags[0].id , test_user.oauth_id, "tag")
#     responseT2 = note_service.get_note_items(test_tags[1].id,  test_user.oauth_id, "tag")
#     assert responseT1.data['notes'][0].content == "Changed 3!!"
#     assert responseT2.data['notes'][0].content == "Changed 4!!"
    
    
def intermitent_save(response: NoteItemsResponse, list_id, list_type, test_user, note_service) -> NoteItemsResponse:
    requestT2: CreateNoteGroup = convert_response_to_request(response, list_id, list_type)
    note_service.update_note_items_sort_order(requestT2, test_user.oauth_id, list_type)
    return note_service.get_note_items(list_id,  test_user.oauth_id, list_type)
    
    
def convert_response_to_request(response: NoteItemsResponse, parent_id, list_type) -> CreateNoteGroup:
    if not response.data['notes']:
        return None
    i: List[NoteResponse] = []
    createGroup = CreateNoteGroup(
        parent_tag_id=parent_id,
        parent_list_type=list_type,
        items=[]
    )
    items = response.data['notes']
    for item in items:
        createGroup.items.append(
            NoteItem(
                content=item.content,
                id=item.id,
                tags=item.tags,
                creation_list_id=item.creation_list_id,
                creation_type=item.creation_type,
                position=None ,
                origin_sort_order=item.origin_sort_order,          
        ))
    return createGroup
        
   
    
    #create 3 note items and two tags, tag the first 2 with first tag, the last two with the second tab
    #get the first tag page, make sure in the right order, modify first item text and save
    #get the second tag page, make sure in the right order, modify first item and save
    #open note page check in right order, open 1st tag check if in right order, open 2nd tag check if in right order
    
    
    
    
    #create 2 note items in a fixture for a note.id
 
    # updated_item = next(item for item in result["created_note_items"] 
    #                    if item.id == test_note_items[0].id)
    # assert updated_item.content == "Updated content"
    # assert updated_item.sequence_number == 10
    
    # # Check that a new item was created
    # new_item = next(item for item in result["created_note_items"] 
    #                if item.id != test_note_items[0].id)
    # assert new_item.content == "Brand new item"
    
    # # Get the associations for the updated item to verify tags
    # assoc_query = select(
    #     NoteItemList.list_id,
    #     NoteItemList.list_type
    # ).where(NoteItemList.note_item_id == test_note_items[0].id)
    
    # associations = note_service.db.execute(assoc_query).fetchall()
    # tag_assocs = [list_id for list_id, list_type in associations if list_type == "tag"]
    
    # # Should have associations to both tags
    # assert len(tag_assocs) == 2
    # assert test_tags[0].id in tag_assocs
    # assert test_tags[1].id in tag_assocs