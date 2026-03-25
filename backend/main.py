from fastapi import FastAPI
from src.api.routes import router
from src.dataBase.dependencies import get_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",     # добавьте эту строку для фронтенда
    "http://localhost:8080",     # порт вашего сервера
    # Если используете React/Vue с другими портами, добавьте их
    "http://localhost:3001",
    "http://localhost:5173",     # для Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # список разрешенных источников
    allow_credentials=True,
    allow_methods=["*"],  # разрешить все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # разрешить все заголовки
)

app.include_router(router)

db = get_db()

@app.on_event("startup")
async def startup_event():
    db.openConnection()

@app.on_event("shutdown")
async def startup_event():
    db.closeConnection()