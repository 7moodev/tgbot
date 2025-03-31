from fastapi import FastAPI, Request
from backend.api.routes import router
from backend.bot.main2 import main as telegram_main, application
from telegram import Update
import asyncio
import os
import json
from contextlib import asynccontextmanager

TOKEN= os.environ.get('tgTOKEN')
BOT_USERNAME= os.environ.get('tgNAME')   # tgNAME
if not TOKEN:
    TOKEN = os.environ.get('tgbot')
PORT = int(os.environ.get('PORT', 8443))
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔁 Launching Telegram bot...")
    asyncio.create_task(telegram_main())
    yield
    print("🛑 Shutting down Telegram bot...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    if application is None:
        return {"status": "bot not ready"}

    raw_data = await request.body()
    update = Update.de_json(json.loads(raw_data), application.bot)
    await application.process_update(update)
    return {"status": "ok"}
