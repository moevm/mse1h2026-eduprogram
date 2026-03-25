from fastapi import FastAPI
from .api.routes import router
from .dataBase.dependencies import get_db

app = FastAPI()
app.include_router(router)

db = get_db()


@app.on_event("startup")
async def startup_event():
    db.openConnection()


@app.on_event("shutdown")
async def shutdown_event():
    db.closeConnection()
