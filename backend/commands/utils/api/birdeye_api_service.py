import requests
import os

from .entities.token_overview_entity import ApiResponse, TokenOverviewEntity
from ..services.log_service import LogService

birdeyeapi = os.environ.get('birdeyeapi')
CHAIN = "solana"
BASE_URL = "https://public-api.birdeye.so"

logger = LogService()

class BirdeyeApiService:
  def __init__(self):
    self.headers = {
        "accept": "application/json",
        "chain": CHAIN,
        "X-API-KEY": birdeyeapi
    }

  async def get_token_overview(self, token:str=None) -> ApiResponse[TokenOverviewEntity]:
      """
      https://docs.birdeye.so/reference/get_defi-token-overview
      Get the overview of a token
      Costs 20 credits per request
      """
      logger.log("Getting token overview for", token)
      if token is None:
          return None

      url = f"{BASE_URL}/defi/token_overview?address={token}"
      response = requests.get(url, headers=self.headers)
      logger.log("Returning token overview for", token)
      return response.json()


if __name__ == "__main__":
  async def call():
    service = BirdeyeApiService()
    response = await service.get_token_overview("0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9")
    response.data
  call()
