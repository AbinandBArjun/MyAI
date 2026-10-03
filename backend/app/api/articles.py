from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.article import Article


router = APIRouter()


@router.get("/")
def get_articles(
    db: Session = Depends(get_db)
):
    articles = (
        db.query(Article)
        .order_by(Article.id.desc())
        .all()
    )

    return articles


@router.get("/{article_id}")
def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    article = (
        db.query(Article)
        .filter(Article.id == article_id)
        .first()
    )

    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found"
        )

    return article