# Notes API

A simple REST API for managing notes, built with FastAPI and SQLite.

## Features

- Create notes
- List all notes
- Get a specific note
- Delete notes
- Automatic API documentation (Swagger UI)
- Full test coverage
- CI/CD with GitHub Actions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

- `GET /` - Welcome message
- `POST /notes` - Create a new note
- `GET /notes` - List all notes
- `GET /notes/{note_id}` - Get a specific note
- `DELETE /notes/{note_id}` - Delete a note

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

## CI/CD

GitHub Actions runs tests automatically on:
- Pushes to `master` or `dev` branches
- Pull requests to `master` or `dev` branches

## Development

The project structure:
```
notes-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and endpoints
│   ├── models.py        # Pydantic models
│   └── database.py      # SQLAlchemy setup
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Test suite
├── requirements.txt
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions config
└── README.md
```
