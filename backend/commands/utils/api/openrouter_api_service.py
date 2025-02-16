import os
from dotenv import load_dotenv

from backend.commands.utils.api.entities.openrouter_entities import OpenRouterMessage, OpenRouterResponse


load_dotenv()

BASE_URL = "https://openrouter.ai/api"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL")
OPENROUTER_HTTP_REFERER = os.environ.get("OPENROUTER_HTTP_REFERER")
OPENROUTER_TITLE = os.environ.get("OPENROUTER_TITLE")

MODEL = OPENROUTER_MODEL or "openai/gpt-4o"


import requests
import json

class OpenRouterApiClient():
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": OPENROUTER_HTTP_REFERER,
            "X-Title": OPENROUTER_TITLE,
            'Content-Type': 'application/json',
        },

    async def chat(self, messages: OpenRouterMessage) -> OpenRouterResponse:
        url = f"{self.base_url}/v1/chat/completions"
        response = await requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps({
                "model": MODEL,
                "messages": messages
            })
        )
        return response

openRouterApiClient = OpenRouterApiClient()

if __name__ == "__main__":
    response = openRouterApiClient.chat([
        {
            "role": "user",
            "content": "Say Hi"
        }
    ])
    print(response.json())

