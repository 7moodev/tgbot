from dataclasses import dataclass
from typing import Optional, TypeVar, Generic
from enum import Enum

T = TypeVar("T")


@dataclass
class ApiResponse(Generic[T]):
    data: T
    success: Optional[bool] = None
    message: Optional[str] = None
    status_code: Optional[int] = None


@dataclass
class SortBy(Enum):
    LIQUIDITY = "liquidity"
    VOLUME24HUSD = "volume"
    RANK = "rank"


@dataclass
class SortType(Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class ApiRequestParams:
    sort_by: Optional[SortBy] = "rank"
    sort_type: Optional[SortType] = "desc"
    limit: Optional[int] = 10
    offset: Optional[int] = 0


DEFAULT_PARAMS = ApiRequestParams()
