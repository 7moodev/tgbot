from fastapi import FastAPI
from backend.api.routes import router
from backend.bot.main2 import main

app = FastAPI()
app.include_router(router)

# Run with: uvicorn app.main:app --reload



