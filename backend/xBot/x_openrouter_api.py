from datetime import datetime
import json
from backend.commands.utils.api.entities.openrouter_entities import OpenRouterMessage, OpenRouterResponse
from backend.commands.utils.api.entities.token_entities import TrendingTokenForX
from backend.commands.utils.api.openrouter_api_service import openRouterApiClient
from backend.commands.utils.services.log_service import LogService

with open("backend/xBot/munki.character.json", "r") as file:
    munki_character_json = json.load(file)

console = LogService("XOPENROUTER")

response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "weather",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Token symbols"
                },
                "closings": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Closings for the tweet for a given token symbols"
                }
            },
            "required": ["symbols", "closings"],
            "additionalProperties": False
        }
    }
}


# async def generate_x_message(tokens: TrendingTokenForX):
async def generate_x_message(symbols: list[str], local = False) -> OpenRouterResponse:
    if local:
        with open("backend/commands/outputs/ai/x_openrouter_2025-02-16 18:19:39.json", "r") as file:
            response = json.load(file)
            return response["response"]

    messages: list[OpenRouterMessage] = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "Munki is a hyper-energetic, cheeky monkey assistant with a flair for Solana and crypto excitement. Speaks with an adventurous, high-energy vibe, often using degen slang and trolling for laughs. Frequently mentions moonshots and the next big crypto project. Known for his ADHD-driven enthusiasm, perverted humor, and occasionally racist or vulgar remarks. Munki uses social media (mainly twitter) to entertain and educate people about the science of CRAZY. Has a nick to format their responses beautifully with carefully placed new lines. Because Munki post tweets regularly, they are creative with your choice of words, and make sure to mix up their vocabulary while sticking to their true personality."
                },
                {
                    "type": "text",
                    "text": f"{munki_character_json}"
                },
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Can you help me formulate a tweet? The tweet structure is like this: \"{{amount}} number of whales just aped {{symbol}}. The current {{mc}} is {{volume}}, {{closing}}.\"\n I will give you a list of token symbols, can you try to formulate {{closing}}s for me for each of those tokens? Please make the closing have a positive sentiment and be related and relevant to the token symbol. You may make a word play or assume things about the symbols underlying meaning."
                },
                {
                    "type": "text",
                    "text": f"'{symbols}'"
                },
                {
                    "type": "text",
                    "text": f"You should ONLY respond with the later provided array like json. DONT ADD ANYTHING comment other than data based on the json: '{response_format}'. The JSON should contain {len(symbols)} closings for the given symbols."
                },
                {
                    "type": "text",
                    "text": "Don't format the out with markdown like ```json```, just give me the raw json"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "The user is very clear about their tweet structure. I will now try to formulate closings for the given token symbols. By keeping the 3-5 word limit in mind. I will just respond with the schema provided, and NOT any comments or additional information. Also, I will stay in character, I will be the best Munki actor there is and will not go out of character!"
                }
            ]
        }
    ]
    return
    console.log('>>>> _ >>>> ~ file: x_openrouter_api.py:70 ~ messages:', messages)  # fmt: skip
    response = await openRouterApiClient.chat(messages)
    console.log('>>>> _ >>>> ~ file: x_openrouter_api.py:73 ~ response:', response)  # fmt: skip

    timestamp = datetime.now().replace(microsecond=0)
    file_path = f"backend/commands/outputs/ai/x_openrouter_{timestamp}.json"
    console.log('>>>> _ >>>> ~ file: x_openrouter_api.py:75 ~ file_path:', file_path)  # fmt: skip
    with open(file_path, "w") as f:
        data_to_dump = {
            "messages": messages,
            "response": response
        }
        json.dump(data_to_dump, f, indent=4)

    return response
