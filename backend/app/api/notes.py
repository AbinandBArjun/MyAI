from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate

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

    return new_note

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

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted"
    }