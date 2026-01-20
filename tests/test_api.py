import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Notes API"}


def test_create_note(client):
    response = client.post(
        "/notes",
        json={"title": "Test Note", "content": "This is a test note"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"
    assert "id" in data
    assert "created_at" in data


def test_get_notes_empty(client):
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_notes(client):
    # Create a couple of notes
    client.post("/notes", json={"title": "Note 1", "content": "Content 1"})
    client.post("/notes", json={"title": "Note 2", "content": "Content 2"})
    
    response = client.get("/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Note 1"
    assert data[1]["title"] == "Note 2"


def test_get_note_by_id(client):
    # Create a note
    create_response = client.post(
        "/notes",
        json={"title": "Specific Note", "content": "Specific Content"}
    )
    note_id = create_response.json()["id"]
    
    # Get the note by ID
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Specific Note"


def test_get_note_not_found(client):
    response = client.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note(client):
    # Create a note
    create_response = client.post(
        "/notes",
        json={"title": "To Delete", "content": "Will be deleted"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404


def test_delete_note_not_found(client):
    response = client.delete("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
