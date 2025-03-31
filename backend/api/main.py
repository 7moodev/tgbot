from fastapi import FastAPI
from backend.api.routes import router
from backend.bot.main2 import main
import asyncio
app = FastAPI()
app.include_router(router)

# Run with: uvicorn app.main:app --reload


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(main())
