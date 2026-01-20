"""
===============================================================================
DATABASE LAYER - PERSISTENCE AND ORM
===============================================================================

Module: app.database
Purpose: Database connection management, ORM models, and session handling
Author: Notes API Team
Last Updated: 2025-01-21

ARCHITECTURAL CONTEXT
---------------------
This module provides the persistence layer for the Notes API. It manages all
interactions with the SQLite database using SQLAlchemy ORM, handling connection
lifecycle, session management, and data model definitions.

C4 MODEL MAPPING
----------------
@c4-container: Database Layer
@c4-technology: Python 3.12, SQLAlchemy 2.0, SQLite 3
@c4-description: ORM-based persistence layer managing note storage and retrieval
@c4-responsibilities:
    - Maintain database connection and session lifecycle
    - Define database schema through ORM models
    - Provide database session to API endpoints
    - Initialize database schema on application startup
    - Abstract SQL queries behind Python objects

DESIGN DECISIONS
----------------
1. **Database Choice: SQLite**
   - Rationale: Zero-configuration, perfect for simple applications
   - Rationale: File-based storage, no separate database server needed
   - Rationale: ACID compliance for data integrity
   - Trade-off: Limited concurrency (single-writer lock)
   - Trade-off: Not suitable for high-traffic production deployments
   - Production Alternative: PostgreSQL or MySQL for multi-user scenarios
   - Use Case: Development, testing, small single-user deployments

2. **ORM Choice: SQLAlchemy 2.0**
   - Rationale: Industry-standard Python ORM with excellent documentation
   - Rationale: Type-safe queries with modern 2.0 API
   - Rationale: Automatic SQL generation reduces errors
   - Rationale: Database agnostic (easy to switch to PostgreSQL later)
   - Trade-off: Slight performance overhead vs raw SQL
   - Alternative Considered: Direct SQL with aiosqlite (rejected for simplicity)

3. **Session Management Pattern**
   - Pattern: Dependency injection via get_db() generator
   - Rationale: Automatic session cleanup (even on exceptions)
   - Rationale: Each request gets isolated database session
   - Rationale: Prevents session leaks and connection pool exhaustion
   - Implementation: Python generator with try/finally ensures cleanup

4. **Schema Initialization**
   - Strategy: Automatic table creation via Base.metadata.create_all()
   - Behavior: Creates tables only if they don't exist (idempotent)
   - Timing: On application startup (via lifespan manager)
   - Future: Replace with Alembic migrations for schema versioning

5. **Timezone Handling**
   - Decision: Use timezone-aware UTC timestamps
   - Rationale: Prevents Python 3.12+ deprecation warnings
   - Rationale: Explicit timezone handling prevents ambiguity
   - Implementation: datetime.now(timezone.utc) instead of deprecated utcnow()
   - Storage: SQLite stores as UTC ISO8601 strings

SYSTEM INTERACTIONS
-------------------
@c4-uses: SQLite Database - "Reads and writes note data" - "SQL/SQLite3"
@c4-used-by: API Application (app.main) - "Requests database sessions" - "SQLAlchemy ORM"

DATABASE SCHEMA
---------------
Table: notes
Columns:
    - id (INTEGER): Primary key, auto-increment
    - title (TEXT): Note title, indexed for search performance
    - content (TEXT): Note content (unlimited length in SQLite)
    - created_at (DATETIME): UTC timestamp, auto-set on creation

Indexes:
    - PRIMARY KEY on id (automatic)
    - INDEX on title (for future search functionality)

PERFORMANCE CONSIDERATIONS
---------------------------
- Connection pooling: NullPool for SQLite (single connection)
- Check same thread: Disabled for multi-threaded FastAPI compatibility
- Query optimization: Primary key lookups are O(log n) via B-tree index
- Pagination: Uses OFFSET/LIMIT (works well for small datasets)

FUTURE ENHANCEMENTS
-------------------
- [ ] Implement Alembic migrations for schema versioning
- [ ] Add full-text search index on title and content
- [ ] Implement soft deletes with 'archived_at' column
- [ ] Add 'updated_at' timestamp with automatic updates
- [ ] Consider adding user_id for multi-tenancy
- [ ] Add database connection pooling for production
- [ ] Implement read replicas for scaling read-heavy workloads

================================================================================
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

# Database URL Configuration
# ---------------------------
# Format: sqlite:///./notes.db
# - sqlite:/// = SQLite database (file-based)
# - ./ = Current working directory
# - notes.db = Database file name
#
# The database file will be created in the directory where the app is run.
# For production, consider using absolute paths or environment variables.
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"

# Database Engine Creation
# -------------------------
# The engine is the starting point for any SQLAlchemy application.
# It manages connections to the database.
#
# Configuration:
# - check_same_thread=False: Required for SQLite with multi-threaded servers
#   SQLite is usually single-threaded, but FastAPI runs on multiple threads
#   This setting makes SQLite thread-safe for our use case
#
# Note: For production with PostgreSQL/MySQL, this connect_args would change
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session Factory
# ---------------
# SessionLocal is a factory for creating database sessions.
# Each session represents a "workspace" for database operations.
#
# Configuration:
# - autocommit=False: Requires explicit db.commit() (safer, more control)
# - autoflush=False: Manual control over when queries are sent to DB
# - bind=engine: Associates sessions with our database engine
#
# Sessions are created per-request and automatically cleaned up
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base
# ----------------
# Base class for all ORM models. All database tables inherit from this.
# Provides metadata and mapping capabilities for SQLAlchemy 2.0
Base = declarative_base()


class NoteDB(Base):
    """
    Note ORM Model
    
    Represents the 'notes' table in the database. Maps Python objects to
    database rows, enabling object-oriented database interactions.
    
    DESIGN CHOICES
    --------------
    1. Separate from Pydantic models (NoteCreate, Note) for separation of concerns
       - NoteDB: Database representation (ORM)
       - Note: API response representation (Pydantic)
       - NoteCreate: API request representation (Pydantic)
    
    2. Auto-incrementing primary key for simplicity
       - Alternative: UUIDs for distributed systems (overkill for this app)
    
    3. No foreign keys yet (single table)
       - Future: Could add user_id for multi-user support
       - Future: Could add tags table with many-to-many relationship
    
    4. Text fields use SQLite's TEXT type (no length limit)
       - SQLite doesn't enforce VARCHAR limits anyway
       - Application-level validation via Pydantic
    
    @c4-component: Note Data Model
    @c4-technology: SQLAlchemy ORM
    
    Attributes:
        id: Unique identifier, automatically assigned by database
        title: Note title, indexed for search performance
        content: Note content, unlimited length
        created_at: UTC timestamp, set automatically on creation
    """
    
    __tablename__ = "notes"
    
    # Primary Key
    # -----------
    # Integer primary key with autoincrement
    # SQLite optimizes primary key lookups via B-tree index
    id = Column(Integer, primary_key=True, index=True)
    
    # Title Field
    # -----------
    # Indexed for future search functionality
    # No length constraint (SQLite TEXT type)
    # Application validates via Pydantic (could add max length)
    title = Column(String, index=True)
    
    # Content Field
    # -------------
    # Main note content, no length limit
    # SQLite TEXT can store up to 2GB
    # Consider adding full-text search index for large datasets
    content = Column(String)

    # Created Timestamp
    # -----------------
    # Timezone-aware UTC timestamp
    # Automatically set on row creation
    # Stored as ISO8601 string in SQLite ("YYYY-MM-DD HH:MM:SS.ffffff+00:00")
    #
    # Note: Using lambda to call datetime.now(timezone.utc) on each insert
    # This ensures the timestamp is generated at insertion time, not at
    # server startup
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    """
    Database Session Dependency
    
    FastAPI dependency that provides a database session to endpoint handlers.
    Implements the dependency injection pattern with automatic cleanup.
    
    LIFECYCLE
    ---------
    1. Create new session when endpoint is called
    2. Yield session to endpoint handler (dependency injection)
    3. Endpoint handler uses session for queries
    4. Finally block ensures session is closed (even if exception occurs)
    
    TRANSACTION MANAGEMENT
    ----------------------
    - Endpoint is responsible for calling db.commit()
    - Uncommitted changes are rolled back on session close
    - Exceptions trigger automatic rollback
    
    THREAD SAFETY
    -------------
    - Each request gets its own session
    - No session sharing between requests
    - Safe for concurrent requests
    
    @c4-provides: Database session for request handling
    
    Yields:
        Session: SQLAlchemy session for database operations
        
    Example Usage:
        @app.get("/notes")
        def get_notes(db: Session = Depends(get_db)):
            return db.query(NoteDB).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Cleanup: Always close session, even if exception occurred
        # This prevents connection leaks and ensures proper resource cleanup
        db.close()


def init_db():
    """
    Initialize Database Schema
    
    Creates all tables defined by ORM models if they don't already exist.
    This is called once on application startup.
    
    BEHAVIOR
    --------
    - Idempotent: Safe to call multiple times (won't recreate existing tables)
    - Creates tables in dependency order (respects foreign keys)
    - Uses engine's metadata to determine what needs creation
    
    LIMITATIONS
    -----------
    - Does NOT handle schema migrations (adding/removing columns)
    - Does NOT version the schema
    - For production, use Alembic for proper migration management
    
    FUTURE
    ------
    Replace with Alembic migrations to support:
    - Schema versioning
    - Rollback capability  
    - Column additions/modifications
    - Data migrations
    
    @c4-initializes: Database schema on application startup
    
    Example:
        # In app startup
        init_db()  # Creates 'notes' table if it doesn't exist
    """
    # Create all tables defined in Base's metadata
    # Only creates tables that don't already exist (safe to call repeatedly)
    Base.metadata.create_all(bind=engine)
