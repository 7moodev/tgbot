from fastapi import FastAPI
from backend.api.routes import router
from backend.bot.main2 import main as telegram_main
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(telegram_main())
    yield
    # Shutdown (optional cleanup)
    # e.g., bot.stop() or database.close()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
