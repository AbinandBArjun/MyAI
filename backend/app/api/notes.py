from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate
from app.services.embedding_service import (
    save_embedding,
    delete_embedding
)

router = APIRouter()


@router.get("/")
def get_notes(db: Session = Depends(get_db)):
    notes = db.query(Note).all()
    return notes


@router.post("/")
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db)
):
    new_note = Note(
        title=note.title,
        content=note.content
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    # Generate and store the note embedding
    text = f"{new_note.title}\n{new_note.content}"

    save_embedding(
        db=db,
        document_type="NOTE",
        document_id=new_note.id,
        text=text
    )

    return new_note


@router.put("/{note_id}")
def update_note(
    note_id: int,
    updated_note: NoteCreate,
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(
        Note.id == note_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    note.title = updated_note.title
    note.content = updated_note.content

    db.commit()
    db.refresh(note)

    # Regenerate the embedding after updating the note
    text = f"{note.title}\n{note.content}"

    save_embedding(
        db=db,
        document_type="NOTE",
        document_id=note.id,
        text=text
    )

    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(
        Note.id == note_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    delete_embedding(
        db=db,
        document_type="NOTE",
        document_id=note.id
    )

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted"
    }