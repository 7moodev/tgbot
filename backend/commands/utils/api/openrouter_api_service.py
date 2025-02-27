import asyncio
import os
from dotenv import load_dotenv

from backend.commands.utils.api.entities.openrouter_entities import OpenRouterMessage, OpenRouterResponse, OpenRouterResponseFormat
from backend.commands.utils.services.log_service import LogService



load_dotenv()

BASE_URL = "https://openrouter.ai/api"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL")
OPENROUTER_HTTP_REFERER = os.environ.get("OPENROUTER_HTTP_REFERER")
OPENROUTER_TITLE = os.environ.get("OPENROUTER_TITLE")

MODEL = OPENROUTER_MODEL or "deepseek/deepseek-r1-distill-llama-70b:free"

console = LogService("OPENROUTER_API")

import requests
import json

class OpenRouterApiClient():
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": OPENROUTER_HTTP_REFERER,
            "X-Title": OPENROUTER_TITLE,
            'Content-Type': 'application/json'
        }

    async def chat(self, messages: list[OpenRouterMessage], response_format: OpenRouterResponseFormat = None) -> OpenRouterResponse:
        url = f"{self.base_url}/v1/chat/completions"
        console.log('>>>> _ >>>> ~ file: openrouter_api_service.py:34 ~ url:', url)  # fmt: skip
        console.log('>>>> _ >>>> ~ file: openrouter_api_service.py:39 ~ self.headers:', self.headers)  # fmt: skip
        response_raw = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps({
                "model": MODEL,
                "messages": messages,
                "response_format": response_format
            })
        )
        response = response_raw.json()
        return response

openRouterApiClient = OpenRouterApiClient()

if __name__ == "__main__":
    async def init():
        response = await openRouterApiClient.chat([
            {
                "role": "user",
                "content": "Say Hi"
            }
        ])
        print(response)
    asyncio.run(init())


# python -m backend.commands.utils.api.openrouter_api_service
