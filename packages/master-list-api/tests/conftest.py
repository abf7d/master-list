import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool

# Import your SQLAlchemy models and Base
from db_init.schemas import Base
from services.note_service import NoteService

import uuid
from datetime import datetime
from db_init.schemas import User, Tag, Note, NoteItem, NoteItemList


# Use a simpler approach with a real PostgreSQL database
# Make sure this database exists or you have permissions to create it
# TEST_DB_URL = "postgresql://postgres:postgres@localhost:5432/test_note_app"
TEST_DB_URL = "postgresql://test_user:test_password@localhost:5433/test_db"

@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLAlchemy engine for the test database."""
    engine = create_engine(
        TEST_DB_URL,
        poolclass=NullPool,  # Disable connection pooling for tests
    )
    
    # Drop and recreate all tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Clean up after tests
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test."""
    # Create a new session
    connection = db_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    # Rollback and close the session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def note_service(db_session):
    """Create a NoteService instance for testing."""
    service = NoteService(db_session)
    return service

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        oauth_id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user
@pytest.fixture

def test_note(db_session, test_user):
    """Create a test note."""
    note = Note(
        id=uuid.uuid4(),
        title="Test Note",
        description="Test description",
        created_at=datetime.utcnow(),
        created_by=test_user.oauth_id
    )
    db_session.add(note)
    db_session.commit()
    return note

@pytest.fixture
def test_tags(db_session, test_user):
    """Create test tags."""
    tag1 = Tag(
        id=uuid.uuid4(),
        name="tag1",
        creation_order=1,
        created_at=datetime.utcnow(),
        created_by=test_user.oauth_id
    )
    tag2 = Tag(
        id=uuid.uuid4(),
        name="tag2",
        creation_order=2,
        created_at=datetime.utcnow(),
        created_by=test_user.oauth_id
    )
    db_session.add_all([tag1, tag2])
    db_session.commit()
    return [tag1, tag2]

@pytest.fixture
def test_note_items(db_session, test_user, test_note, test_tags):
    """Create test note items with associations."""
    item1 = NoteItem(
        id=uuid.uuid4(),
        content="Test content 1",
        created_at=datetime.utcnow(),
        created_by=test_user.oauth_id,
        sequence_number=1
    )
    item2 = NoteItem(
        id=uuid.uuid4(),
        content="Test content 2",
        created_at=datetime.utcnow(),
        created_by=test_user.oauth_id,
        sequence_number=2
    )
    db_session.add_all([item1, item2])
    db_session.flush()
    
    # Create associations
    note_assoc1 = NoteItemList(
        note_item_id=item1.id,
        list_id=test_note.id,
        list_type="note",
        is_origin=True,
        sort_order=1
    )
    tag_assoc1 = NoteItemList(
        note_item_id=item1.id,
        list_id=test_tags[0].id,
        list_type="tag",
        is_origin=False,
        sort_order=None
    )
    note_assoc2 = NoteItemList(
        note_item_id=item2.id,
        list_id=test_note.id,
        list_type="note",
        is_origin=True,
        sort_order=2
    )
    tag_assoc2 = NoteItemList(
        note_item_id=item2.id,
        list_id=test_tags[1].id,
        list_type="tag",
        is_origin=False,
        sort_order=None
    )
    db_session.add_all([note_assoc1, tag_assoc1, note_assoc2, tag_assoc2])
    db_session.commit()
    
    return [item1, item2]



# # Your other fixtures below
# import uuid
# from datetime import datetime
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











# import os
# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, clear_mappers
# from sqlalchemy.pool import NullPool
# from pytest_postgresql import factories

# # Import your SQLAlchemy models and Base
# from db_init.schemas import Base
# from services.note_service import NoteService

# # Use pytest-postgresql for database creation
# @pytest.fixture(scope="session")
# # def postgresql_proc(postgresql_proc_factory):
# def postgresql_proc():
#     """Create a PostgreSQL process instance."""
    
#     postgresql_my_proc = factories.postgresql_proc(
#         port=None, unixsocketdir='/var/run')
    
#     # postgres_proc = postgresql_proc_factory(port=None)
#     yield postgresql_my_proc
#     # postgresql_my_proc.stop()

# @pytest.fixture(scope="session")
# def postgresql(postgresql_proc):
#     """Create a PostgreSQL database."""
#     postgresql = postgresql_proc.cached_postgres
#     yield postgresql

# @pytest.fixture(scope="session")
# def db_engine(postgresql):
#     """Create a SQLAlchemy engine connected to the test database."""
#     engine = create_engine(
#         postgresql.dsn,
#         poolclass=NullPool,  # Disable connection pooling for tests
#     )
#     yield engine
#     engine.dispose()

# @pytest.fixture(scope="function")
# def db_session(db_engine):
#     """Create a new database session for a test."""
#     # Create all tables
#     Base.metadata.create_all(db_engine)
    
#     # Create a new session
#     Session = sessionmaker(bind=db_engine)
#     session = Session()
    
#     yield session
    
#     # Rollback and close the session
#     session.rollback()
#     session.close()

#     # Drop all tables after the test - ensures clean state
#     Base.metadata.drop_all(db_engine)

# @pytest.fixture(scope="function")
# def note_service(db_session):
#     """Create a NoteService instance for testing."""
#     service = NoteService(db_session)
#     return service













# import uuid
# from datetime import datetime
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














#ChatGPT's response after creawting test db

# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from myapp.models import Base

# @pytest.fixture(scope="session")
# def engine():
#     engine = create_engine("postgresql://test_user:test_password@localhost:5433/test_db")
#     Base.metadata.create_all(engine)  # <<<<< This creates tables
#     yield engine
#     engine.dispose()

# @pytest.fixture(scope="function")
# def db_session(engine):
#     connection = engine.connect()
#     transaction = connection.begin()
#     Session = sessionmaker(bind=connection)
#     session = Session()

#     yield session

#     session.close()
#     transaction.rollback()
#     connection.close()