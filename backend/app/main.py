from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.news import router as news_router
from app.api.notes import router as notes_router
from app.api.articles import router as articles_router

app = FastAPI(title="Mypedia API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    notes_router,
    prefix="/notes",
    tags=["Notes"]
)

app.include_router(
    news_router,
    prefix="/news",
    tags=["News"]
)

app.include_router(
    articles_router,
    prefix="/articles",
    tags=["Articles"]
)

@app.get("/")
def home():
    return {"message": "Mypedia Backend Running"}