from app.models.base import Base
from app.models.article import Article
from app.models.note import Note

from app.database.database import engine

Base.metadata.create_all(bind=engine)

print("✅ Tables Created")