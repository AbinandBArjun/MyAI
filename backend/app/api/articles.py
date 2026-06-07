from fastapi import APIRouter, Depends
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