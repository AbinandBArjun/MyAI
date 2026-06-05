from fastapi import FastAPI

from app.api.notes import router as notes_router

app = FastAPI(
    title="Mypedia API"
)

app.include_router(
    notes_router,
    prefix="/notes",
    tags=["Notes"]
)

@app.get("/")
def home():
    return {
        "message": "Mypedia Backend Running"
    }