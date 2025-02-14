from dotenv import load_dotenv
import os
import json
import requests
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import tweepy

load_dotenv()

BASE_URL = "https://api.x.com/2/tweets"
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
client = tweepy.Client(
    consumer_key=os.environ.get("API_KEY"),
    consumer_secret=os.environ.get("API_KEY_SECRET"),
    access_token=os.environ.get("ACCESS_TOKEN"),
    access_token_secret=os.environ.get("ACCESS_TOKEN_SECRET"),
)


@dataclass
class Geo:
    place_id: str


@dataclass
class Media:
    media_ids: List[str]
    tagged_user_ids: List[str]


@dataclass
class Poll:
    duration_minutes: int
    options: List[str]
    reply_settings: str


@dataclass
class Reply:
    exclude_reply_user_ids: List[str]
    in_reply_to_tweet_id: str


@dataclass
class ReplySettings(Enum):
    FOLLOWING = "following"
    MENTIONED_USERS = "mentionedUsers"
    SUBSCRIBERS = "subscribers"


@dataclass
class PostTweetPayload:
    card_uri: Optional[str] = None
    community_id: Optional[str] = None
    direct_message_deep_link: Optional[str] = None
    for_super_followers_only: Optional[bool] = False
    geo: Optional[Geo] = None
    media: Optional[Media] = None
    nullcast: Optional[bool] = False
    poll: Optional[Poll] = None
    quote_tweet_id: Optional[str] = None
    reply: Optional[Reply] = None
    reply_settings: Optional[ReplySettings] = None
    text: str = ""


def post_tweet(tweet_text):
    payload: PostTweetPayload = {"reply_settings": "subscribers", "text": tweet_text}
    response_raw = client.create_tweet(
        reply_settings=payload["reply_settings"], text=payload["text"]
    )
    print(response_raw)
    response = response_raw.json()
    print(response)

    # if response.status_code != 201:
    #     raise Exception(
    #         "Request returned an error: {} {}".format(
    #             response.status_code, response.text
    #         )
    #     )
    print(json.dumps(response, indent=4, sort_keys=True))

    return response


if __name__ == "__main__":
    tweet_text = """
HOLY FUCK, 48 smart wallets aped $SerAlpha ... is this the runner of the day?

The current market cap is $765.0k with $18.2M volume.

Here is the ca: 8GrhA85mcgnaMjyXZ8Hdicayu7byXxbKyEd5UjLnpumpv

---
Find out more at
https://munki.gitbook.io/munki
    """
    try:
        post_tweet(tweet_text)
    except Exception as e:
        print(f"An error occurred: {e}")
    pass

# python -m backend.commands.utils.api.x_api_service
