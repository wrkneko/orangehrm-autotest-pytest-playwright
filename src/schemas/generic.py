from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int


class ApiEnvelope(BaseModel, Generic[T]):
    data: T
    meta: list[Any] = []
    rels: list[Any] = []


class PaginatedApiEnvelope(BaseModel, Generic[T]):
    data: T
    meta: PaginationMeta
    rels: list[Any] = []
