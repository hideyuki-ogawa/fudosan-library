from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class FudosanLibraryError(Exception):
    """Base exception for the fudosan-library package."""


@dataclass(slots=True)
class HTTPError(FudosanLibraryError):
    status_code: int
    message: str
    endpoint_code: Optional[str] = None

    def __str__(self) -> str:
        suffix = f" ({self.endpoint_code})" if self.endpoint_code else ""
        return f"[{self.status_code}] {self.message}{suffix}"


class BadRequestError(HTTPError):
    """Raised for HTTP 400 responses."""


class AuthError(HTTPError):
    """Raised for HTTP 401 responses."""


class NotFoundError(HTTPError):
    """Raised for HTTP 404 responses."""


class RateLimitError(HTTPError):
    """Raised for HTTP 429 responses."""


class ServerError(HTTPError):
    """Raised for HTTP 5xx responses."""


class GeoDependencyError(FudosanLibraryError):
    """Raised when optional geo dependencies are missing."""

    def __init__(self) -> None:
        super().__init__(
            "GeoPandas support requires installing fudosan-library[geo] optional dependencies."
        )
