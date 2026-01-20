"""
================================================================================
DATA MODELS - REQUEST/RESPONSE SCHEMAS
================================================================================

Module: app.models
Purpose: Pydantic models for API request validation and response serialization
Author: Notes API Team
Last Updated: 2025-01-21

ARCHITECTURAL CONTEXT
---------------------
This module defines the data transfer objects (DTOs) used for API communication.
These Pydantic models handle validation, serialization, and documentation of
all data flowing in and out of the API.

C4 MODEL MAPPING
----------------
@c4-component: Data Validation Layer
@c4-technology: Python 3.12, Pydantic 2.0
@c4-description: Schema definitions for API requests and responses with automatic validation
@c4-responsibilities:
    - Validate incoming request data against defined schemas
    - Serialize outgoing response data to JSON
    - Generate JSON Schema for OpenAPI documentation
    - Provide type hints for IDE support and type checking
    - Prevent invalid data from reaching business logic

DESIGN DECISIONS
----------------
1. **Validation Library: Pydantic v2**
   - Rationale: Native FastAPI integration (FastAPI was built for Pydantic)
   - Rationale: Automatic OpenAPI schema generation
   - Rationale: Type-based validation using Python type hints
   - Rationale: Excellent performance (Rust core in v2)
   - Rationale: Clear error messages for API consumers
   - Alternative Considered: Marshmallow (rejected due to manual integration)

2. **Model Separation Strategy**
   - Pattern: Separate models for Create/Update/Response
   - Rationale: Different operations need different fields
   - NoteCreate: Only fields user can provide (title, content)
   - NoteUpdate: All fields optional for partial updates
   - Note: Full response with generated fields (id, created_at)
   - Trade-off: More classes vs single model with complex validation

3. **Optional Fields in Updates**
   - Pattern: All fields optional with None defaults in NoteUpdate
   - Rationale: Enables partial updates (PATCH semantics)
   - Rationale: Client can update just title, just content, or both
   - Implementation: Check for None before updating fields

4. **ORM Mode / from_attributes**
   - Configuration: model_config with from_attributes=True
   - Rationale: Allows Pydantic to read data from ORM objects
   - Enables: return db_note (SQLAlchemy object) directly from endpoint
   - Benefit: Automatic conversion from ORM to Pydantic to JSON
   - Migration: Updated from Pydantic v1's orm_mode to v2's from_attributes

VALIDATION RULES
----------------
Current (Implicit):
- title: Required string (NoteCreate)
- content: Required string (NoteCreate)
- title: Optional string (NoteUpdate)
- content: Optional string (NoteUpdate)

Future Enhancements:
- [ ] Add max length constraints (e.g., title max 200 chars)
- [ ] Add min length constraints (e.g., title min 1 char)
- [ ] Add regex validation for title (e.g., no special chars)
- [ ] Add content type validation (e.g., markdown, plain text)
- [ ] Add custom validators for business rules

SYSTEM INTERACTIONS
-------------------
@c4-used-by: API Application (app.main) - "Validates requests and formats responses"

ERROR HANDLING
--------------
Validation Failures:
- HTTP 422 Unprocessable Entity
- Automatic from FastAPI when request doesn't match schema
- Includes detailed field-level error messages
- Example: {"detail": [{"loc": ["body", "title"], "msg": "field required"}]}

FUTURE ENHANCEMENTS
-------------------
- [ ] Add field-level validation (max lengths, regex patterns)
- [ ] Add custom validators for business rules
- [ ] Add examples in schema for better OpenAPI docs
- [ ] Add tags field (List[str]) for categorization
- [ ] Add archived field (bool) for soft deletes
- [ ] Add updated_at timestamp for tracking modifications
- [ ] Add owner/user_id for multi-user support

================================================================================
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class NoteCreate(BaseModel):
    """
    Note Creation Request Schema

    Defines the data required to create a new note. Only includes fields
    that the user can provide - generated fields (id, timestamps) are excluded.

    USAGE
    -----
    POST /notes endpoint expects request body matching this schema.
    FastAPI automatically validates the request and converts JSON to this model.

    VALIDATION
    ----------
    Current:
    - Both fields are required (no defaults)
    - Must be valid strings
    - No length constraints yet (future enhancement)

    Future Validation Ideas:
    - title: max 200 characters, min 1 character
    - content: max 10,000 characters
    - title: no leading/trailing whitespace
    - content: accept markdown formatting

    @c4-schema: Note creation request

    Attributes:
        title: Note title/heading (required)
        content: Note body/content (required)

    Example:
        {
            "title": "Meeting Notes",
            "content": "Discussed project timeline and deliverables"
        }
    """

    title: str
    content: str

    # Future: Add field validators
    # @validator('title')
    # def title_not_empty(cls, v):
    #     if not v.strip():
    #         raise ValueError('Title cannot be empty or whitespace')
    #     return v.strip()


class NoteUpdate(BaseModel):
    """
    Note Update Request Schema

    Defines the data for updating an existing note. All fields are optional
    to support partial updates (PATCH semantics).

    USAGE
    -----
    Future PATCH /notes/{id} endpoint will use this schema.
    Client can update just the title, just the content, or both.

    VALIDATION
    ----------
    - All fields optional (None if not provided)
    - When field is provided, must be valid string
    - Empty string vs None have different meanings:
      - None: Don't update this field
      - Empty string: Update field to empty (if validation allows)

    UPDATE SEMANTICS
    ----------------
    Partial Update (PATCH):
    - Only provided fields are updated
    - Unprovided fields remain unchanged
    - Enables efficient updates without reading full object first

    @c4-schema: Note update request (partial updates)

    Attributes:
        title: New note title (optional)
        content: New note content (optional)

    Examples:
        Update title only:
        {
            "title": "Updated Meeting Notes"
        }

        Update content only:
        {
            "content": "Added more details about the project timeline"
        }

        Update both:
        {
            "title": "Final Meeting Notes",
            "content": "Complete summary with action items"
        }
    """

    title: Optional[str] = None
    content: Optional[str] = None


class Note(BaseModel):
    """
    Note Response Schema

    Defines the complete note representation returned by the API.
    Includes all fields: user-provided and system-generated.

    USAGE
    -----
    All endpoints that return notes use this schema:
    - GET /notes/{id} - Single note
    - POST /notes - Created note
    - GET /notes - List of notes
    - Future: PATCH /notes/{id} - Updated note

    ORM INTEGRATION
    ---------------
    The from_attributes=True configuration allows this model to be
    instantiated directly from SQLAlchemy ORM objects:

        db_note = db.query(NoteDB).first()  # SQLAlchemy object
        return db_note  # FastAPI converts to Note automatically

    This eliminates manual mapping code and ensures consistency.

    SERIALIZATION
    -------------
    FastAPI automatically serializes this model to JSON:
    - datetime → ISO8601 string ("2025-01-21T10:30:00+00:00")
    - All fields included in response
    - JSON Schema generated for OpenAPI docs

    @c4-schema: Note response (full representation)

    Attributes:
        id: Unique identifier (generated by database)
        title: Note title
        content: Note content
        created_at: UTC timestamp when note was created (generated by database)

    Example:
        {
            "id": 1,
            "title": "Meeting Notes",
            "content": "Discussed project timeline",
            "created_at": "2025-01-21T10:30:00.123456+00:00"
        }
    """

    # Pydantic v2 Configuration
    # -------------------------
    # from_attributes=True: Read data from object attributes (ORM mode)
    # This replaces Pydantic v1's `class Config: orm_mode = True`
    model_config = ConfigDict(from_attributes=True)

    # Response Fields
    # ---------------
    # All fields are required in responses (no Optional)
    # Database guarantees these fields are always present

    id: int
    title: str
    content: str
    created_at: datetime

    # Future: Add computed fields or custom serializers
    # @computed_field
    # @property
    # def excerpt(self) -> str:
    #     """Return first 100 chars of content as preview"""
    #     return self.content[:100] + "..." if len(self.content) > 100 else self.content
