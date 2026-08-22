"""Standardized API response wrapper."""
from __future__ import annotations

import datetime
from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiMeta(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    execution_ms: Optional[float] = None
    version: str = "v1"


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    code: int = 200
    message: str = "OK"
    data: Optional[T] = None
    error: Optional[str] = None
    meta: ApiMeta = Field(default_factory=ApiMeta)

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: str = "Operation completed successfully",
        code: int = 200,
        execution_ms: Optional[float] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> ApiResponse[T]:
        m = ApiMeta(execution_ms=execution_ms)
        if meta and isinstance(meta, dict):
            for k, v in meta.items():
                if hasattr(m, k):
                    setattr(m, k, v)
        return cls(success=True, code=code, message=message, data=data, error=None, meta=m)

    @classmethod
    def fail(
        cls,
        error: Optional[str] = None,
        message: str = "Operation failed",
        code: int = 400,
        data: Optional[T] = None,
        execution_ms: Optional[float] = None
    ) -> ApiResponse[T]:
        m = ApiMeta(execution_ms=execution_ms)
        return cls(success=False, code=code, message=message, data=data, error=error, meta=m)
