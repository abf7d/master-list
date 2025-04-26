
#Added these to conftest.py

# import uuid
# from datetime import datetime

# import pytest
# from db_init.schemas import User, Tag, Note, NoteItem, NoteItemList

# @pytest.fixture
# def test_user(db_session):
#     """Create a test user."""
#     user = User(
#         id=uuid.uuid4(),
#         oauth_id=uuid.uuid4(),
#         email="test@example.com",
#         name="Test User",
#         created_at=datetime.utcnow()
#     )
#     db_session.add(user)
#     db_session.commit()
#     return user

# @pytest.fixture
# def test_tags(db_session, test_user):
#     """Create test tags."""
#     tag1 = Tag(
#         id=uuid.uuid4(),
#         name="tag1",
#         creation_order=1,
#         created_at=datetime.utcnow(),
#         created_by=test_user.oauth_id
#     )
#     tag2 = Tag(
#         id=uuid.uuid4(),
#         name="tag2",
#         creation_order=2,
#         created_at=datetime.utcnow(),
#         created_by=test_user.oauth_id
#     )
#     db_session.add_all([tag1, tag2])
#     db_session.commit()
#     return [tag1, tag2]

# @pytest.fixture
# def test_note(db_session, test_user):
#     """Create a test note."""
#     note = Note(
#         id=uuid.uuid4(),
#         title="Test Note",
#         description="Test description",
#         created_at=datetime.utcnow(),
#         created_by=test_user.oauth_id
#     )
#     db_session.add(note)
#     db_session.commit()
#     return note

# @pytest.fixture
# def test_note_items(db_session, test_user, test_note, test_tags):
#     """Create test note items with associations."""
#     item1 = NoteItem(
#         id=uuid.uuid4(),
#         content="Test content 1",
#         created_at=datetime.utcnow(),
#         created_by=test_user.oauth_id,
#         sequence_number=1
#     )
#     item2 = NoteItem(
#         id=uuid.uuid4(),
#         content="Test content 2",
#         created_at=datetime.utcnow(),
#         created_by=test_user.oauth_id,
#         sequence_number=2
#     )
#     db_session.add_all([item1, item2])
#     db_session.flush()
    
#     # Create associations
#     note_assoc1 = NoteItemList(
#         note_item_id=item1.id,
#         list_id=test_note.id,
#         list_type="note",
#         is_origin=True,
#         sort_order=1
#     )
#     tag_assoc1 = NoteItemList(
#         note_item_id=item1.id,
#         list_id=test_tags[0].id,
#         list_type="tag",
#         is_origin=False,
#         sort_order=None
#     )
#     note_assoc2 = NoteItemList(
#         note_item_id=item2.id,
#         list_id=test_note.id,
#         list_type="note",
#         is_origin=True,
#         sort_order=2
#     )
#     tag_assoc2 = NoteItemList(
#         note_item_id=item2.id,
#         list_id=test_tags[1].id,
#         list_type="tag",
#         is_origin=False,
#         sort_order=None
#     )
#     db_session.add_all([note_assoc1, tag_assoc1, note_assoc2, tag_assoc2])
#     db_session.commit()
    
#     return [item1, item2]