from fastapi import FastAPI

app = FastAPI(
    title="Mypedia API",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Mypedia Backend Running"
    }