from dataclasses import dataclass
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

@dataclass
class ApiResponse(Generic[T]):
  data: T
  success: Optional[bool] = None
  message: Optional[str] = None
