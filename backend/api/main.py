from fastapi import FastAPI
from backend.api.routes import router
from backend.bot.main2 import main as telegram_main
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Launching Telegram bot...")
    asyncio.create_task(telegram_main())  # don't await here!
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)
