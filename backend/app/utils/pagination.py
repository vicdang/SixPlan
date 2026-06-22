import math
from dataclasses import dataclass
from typing import TypeVar, Generic, Sequence

from app.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


@dataclass
class PageParams:
    page: int = 1
    size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        self.page = max(1, self.page)
        self.size = max(1, min(self.size, MAX_PAGE_SIZE))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass
class PaginatedResult(Generic[T]):
    data: Sequence[T]
    page: int
    size: int
    total: int

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.size) if self.size else 0

    def to_dict(self) -> dict:
        return {
            "data": self.data,
            "pagination": {
                "page": self.page,
                "size": self.size,
                "total": self.total,
                "total_pages": self.total_pages,
            },
        }
