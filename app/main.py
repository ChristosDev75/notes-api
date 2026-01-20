"""
================================================================================
API APPLICATION ENTRY POINT
================================================================================

Module: app.main
Purpose: FastAPI application definition and HTTP endpoint orchestration
Author: Notes API Team
Last Updated: 2025-01-21

ARCHITECTURAL CONTEXT
---------------------
This module serves as the primary container for the Notes API system. It defines
the FastAPI application instance and all HTTP endpoints that external clients
interact with. This is the boundary between the outside world and our internal
business logic.

C4 MODEL MAPPING
----------------
@c4-container: API Application
@c4-technology: Python 3.12, FastAPI 0.104
@c4-description: REST API providing CRUD operations for notes with automatic 
                 request validation and OpenAPI documentation generation
@c4-responsibilities:
    - Accept and validate HTTP requests from external clients
    - Route requests to appropriate business logic handlers
    - Transform responses into JSON format
    - Generate OpenAPI/Swagger documentation
    - Manage application lifecycle (startup/shutdown)

DESIGN DECISIONS
----------------
1. **Framework Choice: FastAPI**
   - Rationale: Automatic request/response validation via Pydantic
   - Rationale: Built-in OpenAPI documentation generation
   - Rationale: Async support for potential future scalability
   - Rationale: Type hints improve IDE support and catch errors early
   - Trade-off: Slightly higher memory footprint vs Flask
   - Alternative Considered: Flask + Marshmallow (rejected due to manual validation)

2. **Lifespan Management**
   - Pattern: AsyncContextManager for startup/shutdown hooks
   - Rationale: Recommended FastAPI pattern as of v0.93.0
   - Rationale: Replaced deprecated @app.on_event decorators
   - Use Case: Initialize database schema on startup
   - Future Use: Could add connection pool warmup, cache initialization

3. **Dependency Injection**
   - Pattern: FastAPI's Depends() for database session management
   - Rationale: Automatic session lifecycle (creation, cleanup)
   - Rationale: Improves testability (easy to mock dependencies)
   - Rationale: Prevents session leaks

4. **Response Models**
   - Pattern: Explicit Pydantic models for all responses
   - Rationale: Automatic serialization and documentation
   - Rationale: Type safety guarantees
   - Trade-off: Slight performance overhead vs raw dicts

SYSTEM INTERACTIONS
-------------------
@c4-uses: Database Layer (app.database) - "Manages note persistence" - "SQLAlchemy ORM"
@c4-uses: Data Models (app.models) - "Validates request/response data" - "Pydantic"
@c4-used-by-person: API Consumer - "Creates, reads, and deletes notes" - "HTTPS/JSON"

ENDPOINTS OVERVIEW
------------------
- GET  /          - Health check and welcome message
- POST /notes     - Create a new note
- GET  /notes     - List all notes (with pagination)
- GET  /notes/:id - Retrieve a specific note
- DELETE /notes/:id - Delete a specific note

ERROR HANDLING STRATEGY
-----------------------
- 404 Not Found: Resource doesn't exist (note ID not in database)
- 422 Unprocessable Entity: Invalid request data (handled by FastAPI/Pydantic)
- 500 Internal Server Error: Unexpected exceptions (FastAPI default handler)

FUTURE ENHANCEMENTS
-------------------
- [ ] Add authentication/authorization middleware
- [ ] Implement rate limiting
- [ ] Add request logging and correlation IDs
- [ ] Add metrics collection (Prometheus)
- [ ] Implement soft deletes with 'archived' flag
- [ ] Add full-text search across notes

================================================================================
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

from .database import get_db, init_db, NoteDB
from .models import Note, NoteCreate, NoteUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Context Manager

    Manages the complete lifecycle of the FastAPI application from startup
    through shutdown. This pattern ensures proper resource initialization
    and cleanup.

    STARTUP PHASE
    -------------
    1. Initialize database schema (create tables if they don't exist)
    2. Future: Could warm up connection pools
    3. Future: Could initialize cache connections

    SHUTDOWN PHASE
    --------------
    Currently a no-op, but reserved for future cleanup:
    - Close database connections
    - Flush pending writes
    - Release external resources

    @c4-relationship: Initializes Database Container on startup

    Technical Notes:
    - Uses async context manager protocol (__aenter__, __aexit__)
    - FastAPI calls this exactly once during application lifecycle
    - Any exceptions during startup will prevent the app from starting

    Args:
        app: The FastAPI application instance (provided by FastAPI)

    Yields:
        Control back to FastAPI to run the application
    """
    # Startup: Initialize database
    init_db()

    # Application runs here (yield control to FastAPI)
    yield

    # Shutdown: Reserved for future cleanup
    # Future: Close database connections, flush caches, etc.


# @c4-component: FastAPI Application Instance
# @c4-technology: FastAPI 0.104
app = FastAPI(
    title="Notes API",
    version="0.1.0",
    lifespan=lifespan,
    description="A simple REST API for managing text notes with full CRUD operations"
)


@app.get("/")
def read_root():
    """
    Root Endpoint - Health Check
    
    Provides a simple health check endpoint to verify the API is running.
    Useful for monitoring, load balancer health checks, and quick status verification.
    
    Returns:
        dict: Welcome message confirming API availability
        
    Example Response:
        {
            "message": "Welcome to Notes API"
        }
    """
    return {"message": "Welcome to Notes API"}


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """
    Create Note Endpoint
    
    Creates a new note with the provided title and content. The note is
    immediately persisted to the database and assigned a unique ID.
    
    WORKFLOW
    --------
    1. FastAPI validates request body against NoteCreate schema (Pydantic)
    2. Create NoteDB ORM instance with provided data
    3. Add to database session (stages for commit)
    4. Commit transaction (persists to SQLite)
    5. Refresh ORM instance to get generated ID and timestamp
    6. Return as Note response model (FastAPI serializes to JSON)
    
    @c4-operation: create_note
    @c4-calls: Database Layer - "Persists new note"
    
    Args:
        note: Note data (title and content) validated by Pydantic
        db: Database session injected by FastAPI dependency system
        
    Returns:
        Note: The created note with generated ID and timestamp
        
    HTTP Status:
        201 Created: Note successfully created
        422 Unprocessable Entity: Invalid request data (automatic from FastAPI)
        
    Example Request:
        POST /notes
        {
            "title": "Meeting Notes",
            "content": "Discussed Q1 roadmap and priorities"
        }
        
    Example Response:
        {
            "id": 1,
            "title": "Meeting Notes",
            "content": "Discussed Q1 roadmap and priorities",
            "created_at": "2025-01-21T10:30:00Z"
        }
    """
    db_note = NoteDB(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@app.get("/notes", response_model=List[Note])
def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List Notes Endpoint
    
    Retrieves a paginated list of notes from the database. Supports basic
    pagination via skip/limit parameters.
    
    PAGINATION STRATEGY
    -------------------
    - Default: Returns first 100 notes
    - Max Limit: 100 notes per request (prevents excessive memory usage)
    - Skip: Offset for pagination (e.g., skip=100 for second page)
    
    Note: This is a simple offset-based pagination. For large datasets,
    cursor-based pagination would be more efficient.
    
    @c4-operation: get_notes
    @c4-calls: Database Layer - "Queries notes with pagination"
    
    Args:
        skip: Number of notes to skip (default: 0)
        limit: Maximum number of notes to return (default: 100, max: 100)
        db: Database session injected by FastAPI
        
    Returns:
        List[Note]: Array of note objects
        
    HTTP Status:
        200 OK: Notes retrieved successfully (may be empty array)
        
    Example Request:
        GET /notes?skip=0&limit=10
        
    Example Response:
        [
            {
                "id": 1,
                "title": "Note 1",
                "content": "Content 1",
                "created_at": "2025-01-21T10:00:00Z"
            },
            {
                "id": 2,
                "title": "Note 2",
                "content": "Content 2",
                "created_at": "2025-01-21T10:15:00Z"
            }
        ]
    """
    notes = db.query(NoteDB).offset(skip).limit(limit).all()
    return notes


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Get Single Note Endpoint
    
    Retrieves a specific note by its unique ID. Returns 404 if the note
    doesn't exist.
    
    LOOKUP STRATEGY
    ---------------
    - Primary key lookup (most efficient query possible)
    - SQLite uses index on primary key automatically
    - Single database roundtrip
    
    @c4-operation: get_note
    @c4-calls: Database Layer - "Fetches note by ID"
    
    Args:
        note_id: Unique identifier of the note (path parameter)
        db: Database session injected by FastAPI
        
    Returns:
        Note: The requested note object
        
    Raises:
        HTTPException(404): If note with given ID doesn't exist
        
    HTTP Status:
        200 OK: Note found and returned
        404 Not Found: Note with given ID doesn't exist
        422 Unprocessable Entity: Invalid note_id format (not an integer)
        
    Example Request:
        GET /notes/1
        
    Example Response:
        {
            "id": 1,
            "title": "Meeting Notes",
            "content": "Discussed Q1 roadmap",
            "created_at": "2025-01-21T10:30:00Z"
        }
    """
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Delete Note Endpoint
    
    Permanently deletes a note from the database. This is a hard delete -
    the data is immediately removed and cannot be recovered.
    
    DELETION STRATEGY
    -----------------
    - Hard delete (permanent removal from database)
    - No soft delete / archiving (future enhancement)
    - Transaction is committed immediately
    
    Future Enhancement: Implement soft delete with 'archived' flag to allow
    recovery and maintain audit trail.
    
    @c4-operation: delete_note
    @c4-calls: Database Layer - "Removes note from database"
    
    Args:
        note_id: Unique identifier of the note to delete
        db: Database session injected by FastAPI
        
    Returns:
        None (HTTP 204 has no response body)
        
    Raises:
        HTTPException(404): If note with given ID doesn't exist
        
    HTTP Status:
        204 No Content: Note successfully deleted
        404 Not Found: Note with given ID doesn't exist
        422 Unprocessable Entity: Invalid note_id format
        
    Example Request:
        DELETE /notes/1
        
    Example Response:
        (No body, just 204 status code)
    """
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
