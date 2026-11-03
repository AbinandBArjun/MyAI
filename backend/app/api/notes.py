from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate
from app.services.embedding_service import (
    save_embedding,
    delete_embedding
)
from app.services.chunk_indexing_service import (
    index_document_chunks,
    delete_document_chunks
)

router = APIRouter()


@router.get("/")
def get_notes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Note).order_by(Note.id.desc())

    total_items = query.count()

    total_pages = (
        (total_items + page_size - 1) // page_size
    )

    notes = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": notes,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    }


@router.get("/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


@router.post("/")
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db)
):
    try:
        new_note = Note(
            title=note.title,
            content=note.content
        )

        db.add(new_note)
        db.flush()

        text = f"{new_note.title}\n{new_note.content}"

        save_embedding(
            db=db,
            document_type="NOTE",
            document_id=new_note.id,
            text=text
        )

        index_document_chunks(
            db=db,
            document_type="NOTE",
            document_id=new_note.id,
            title=new_note.title,
            content=new_note.content
        )

        db.commit()
        db.refresh(new_note)

        return new_note

    except Exception:
        db.rollback()
        raise


@router.put("/{note_id}")
def update_note(
    note_id: int,
    updated_note: NoteCreate,
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    try:
        note.title = updated_note.title
        note.content = updated_note.content

        text = f"{note.title}\n{note.content}"

        save_embedding(
            db=db,
            document_type="NOTE",
            document_id=note.id,
            text=text
        )

        index_document_chunks(
            db=db,
            document_type="NOTE",
            document_id=note.id,
            title=note.title,
            content=note.content
        )

        db.commit()
        db.refresh(note)

        return note

    except Exception:
        db.rollback()
        raise


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    try:
        delete_embedding(
            db=db,
            document_type="NOTE",
            document_id=note.id
        )

        delete_document_chunks(
            db=db,
            document_type="NOTE",
            document_id=note.id
        )

        db.delete(note)
        db.commit()

        return {
            "message": "Note deleted"
        }

    except Exception:
        db.rollback()
        raise
