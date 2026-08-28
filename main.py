from fastapi import FastAPI
from routes.tasks import router

app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Task API v1.0.0 is running."}
    