from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db, init_db, NoteDB
from .models import Note, NoteCreate, NoteUpdate

app = FastAPI(title="Notes API", version="0.1.0")


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to Notes API"}


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    db_note = NoteDB(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@app.get("/notes", response_model=List[Note])
def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = db.query(NoteDB).offset(skip).limit(limit).all()
    return notes


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
