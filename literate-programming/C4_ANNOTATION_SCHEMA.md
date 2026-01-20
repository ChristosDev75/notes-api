# C4 Annotation Schema for Literate Python

## Overview

This document defines the annotation schema used to embed C4 model metadata within Python source code. These annotations enable automated generation of C4 diagrams from well-documented codebases.

## Design Philosophy

The annotation schema is designed to be:
- **Non-invasive**: Uses comments and docstrings, doesn't affect code execution
- **Human-readable**: Clear semantic meaning without parsing tools
- **Literate**: Encourages narrative documentation alongside technical specs
- **Extractable**: Structured enough for automated parsing
- **Flexible**: Supports both inline tags and structured documentation

## Annotation Types

### Module-Level Annotations

Placed at the top of Python modules (in module docstring).

#### @c4-container
Declares that this module represents a C4 Container.

```python
"""
@c4-container: API Application
@c4-technology: Python 3.12, FastAPI 0.104
@c4-description: REST API providing CRUD operations for notes
@c4-responsibilities:
    - Accept and validate HTTP requests
    - Route requests to business logic
    - Transform responses to JSON
"""
```

**Fields:**
- `@c4-container`: Container name (required)
- `@c4-technology`: Tech stack description (required)
- `@c4-description`: Brief description (required)
- `@c4-responsibilities`: Bullet list of responsibilities (optional)

#### @c4-component
Declares that this module/class represents a C4 Component.

```python
"""
@c4-component: Data Validation Layer
@c4-technology: Python 3.12, Pydantic 2.0
@c4-description: Schema definitions for API validation
"""
```

**Fields:**
- `@c4-component`: Component name (required)
- `@c4-technology`: Tech stack (required)
- `@c4-description`: Brief description (required)

### Relationship Annotations

Define interactions between C4 elements.

#### @c4-uses
Declares a dependency on another container/component.

```python
"""
@c4-uses: Database Layer (app.database) - "Manages note persistence" - "SQLAlchemy ORM"
@c4-uses: Data Models (app.models) - "Validates requests" - "Pydantic"
```

**Format:**
```
@c4-uses: <target> - "<description>" - "<technology>"
```

- `<target>`: Name of the container/component being used
- `<description>`: What interaction occurs (action phrase)
- `<technology>`: Protocol/technology used for interaction

#### @c4-used-by
Declares usage by another element (inverse relationship).

```python
"""
@c4-used-by: API Application - "Requests database sessions" - "SQLAlchemy ORM"
@c4-used-by-person: API Consumer - "Creates notes via HTTP" - "HTTPS/JSON"
"""
```

**Variants:**
- `@c4-used-by`: Used by another container/component
- `@c4-used-by-person`: Used by an external person/actor

#### @c4-calls
Function/method level annotation for operation calls.

```python
"""
@c4-operation: create_note
@c4-calls: Database Layer - "Persists new note"
"""
def create_note(note: NoteCreate, db: Session):
    ...
```

### Inline Annotations

Shorter annotations for specific code elements.

```python
# @c4-component: FastAPI Application Instance
# @c4-technology: FastAPI 0.104
app = FastAPI(...)
```

## Annotation Placement

### Module Docstring (Top of File)
Place container/component declarations and module-level relationships:

```python
"""
================================================================================
MODULE TITLE
================================================================================

Module: app.main
Purpose: Brief purpose statement

ARCHITECTURAL CONTEXT
---------------------
Narrative explanation of this module's role in the system.

C4 MODEL MAPPING
----------------
@c4-container: API Application
@c4-technology: Python, FastAPI
@c4-description: Main API container
@c4-uses: Database Layer - "Persists data" - "SQLAlchemy"
"""
```

### Class Docstrings
For component-level detail:

```python
class NoteDB(Base):
    """
    Note ORM Model
    
    Represents the 'notes' table in the database.
    
    @c4-component: Note Data Model
    @c4-technology: SQLAlchemy ORM
    """
```

### Function Docstrings
For operation-level detail:

```python
def create_note(note: NoteCreate, db: Session):
    """
    Create Note Endpoint
    
    Workflow explanation...
    
    @c4-operation: create_note
    @c4-calls: Database Layer - "Persists new note"
    """
```

### Inline Comments
For simple declarations:

```python
# @c4-component: Application Instance
# @c4-technology: FastAPI
app = FastAPI(...)
```

## Literate Documentation Guidelines

### Structure

Each module should follow this structure:

1. **Module Header** (separators, title, metadata)
2. **Architectural Context** - Why this module exists
3. **C4 Model Mapping** - Structured C4 annotations
4. **Design Decisions** - Architecture Decision Records (ADRs)
5. **System Interactions** - Relationship annotations
6. **Implementation Details** - Technical specifics
7. **Future Enhancements** - Planned improvements

### Writing Style

**DO:**
- Write in narrative prose explaining "why" not just "what"
- Explain design decisions and trade-offs
- Document alternatives considered
- Use clear section headers
- Include examples
- Reference specific line numbers or code sections
- Explain future enhancement plans

**DON'T:**
- Repeat what the code already says
- Write generic boilerplate
- Use jargon without explanation
- Assume reader knows the context
- Skip the "why" behind decisions

### Example: Good vs Bad

**Bad (Just restates code):**
```python
"""
This module contains the database code.
It uses SQLAlchemy.
"""
```

**Good (Explains context and decisions):**
```python
"""
DATABASE LAYER - PERSISTENCE AND ORM

This module provides the persistence layer using SQLAlchemy ORM.

DESIGN DECISION: SQLite
We chose SQLite for its zero-configuration setup, making it ideal
for development and small deployments. For production with >100 concurrent
users, we recommend PostgreSQL due to SQLite's single-writer limitation.

@c4-container: Database Layer
@c4-technology: SQLAlchemy 2.0, SQLite 3
@c4-uses: SQLite Database - "Persists note data" - "SQL"
"""
```

## Extracting C4 Models

A tangler tool will parse these annotations to generate C4 DSL. The extraction process:

1. **Parse Module Docstrings** - Extract container/component declarations
2. **Parse Relationship Annotations** - Build interaction graph
3. **Parse Narrative Documentation** - Extract design decisions and context
4. **Generate C4 DSL** - Map to Structurizr DSL format

## Example: Complete Module

See `app/main.py`, `app/database.py`, and `app/models.py` for complete examples of literate, annotated Python modules.

## Future Extensions

### Planned Annotation Types

- `@c4-deployment-node`: For deployment architecture
- `@c4-database`: For data stores
- `@c4-external-system`: For external dependencies
- `@c4-security-boundary`: For security zones
- `@c4-async`: For asynchronous interactions

### Planned Metadata

- `@c4-performance`: Performance characteristics
- `@c4-scalability`: Scaling limits and strategies
- `@c4-reliability`: Failure modes and recovery
- `@c4-security`: Security considerations

## References

- C4 Model: https://c4model.com/
- Structurizr DSL: https://github.com/structurizr/dsl
- Literate Programming: http://www.literateprogramming.com/
