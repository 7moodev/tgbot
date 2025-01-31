
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserLogEntity:
    id: int
    username: str
    user_id: str
    coin_address: str
    command_name: str
    command_result: Optional[str]  # Nullable field
    timestamp: str  # Stored as string in ISO format

default_user_log_entity = UserLogEntity(
    id=-1,
    username="user123",
    user_id="id123",
    coin_address="0xABC123...",
    command_name="check_balance",
    command_result="Balance: 100 tokens",
    timestamp="2025-01-30 12:34:56"
)
