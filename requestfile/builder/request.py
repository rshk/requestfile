from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

from multidict import CIMultiDict, MultiDict


@dataclass(slots=True)
class Request:
    method: str | None = None
    url: str | None = None

    # HTTP headers
    headers: CIMultiDict[str | bytes] = field(default_factory=lambda: CIMultiDict())

    # Cookies
    cookies: MultiDict[str | bytes] = field(default_factory=lambda: MultiDict())

    # URL query parameters
    params: MultiDict[str | bytes] = field(default_factory=lambda: MultiDict())

    # Form fields
    fields: MultiDict[str | bytes] = field(default_factory=lambda: MultiDict())

    # Multipart form "parts"
    files: MultiDict[PartData] = field(default_factory=lambda: MultiDict())

    # Items used to build the body data, based on content_type
    body_data: list[BodyItem] = field(default_factory=list)

    # Raw body data
    raw_body: str | bytes | None = None

    # Guessed content type for the request
    content_type: RequestContentType | None = None


class RequestContentType(Enum):
    # Binary data (any content-type)
    BYTES = "bytes"

    # Text data (any content-type)
    TEXT = "text"

    # Form data: application/x-www-form-urlencoded
    # Raw data will be parsed as encoded form data
    FORM = "form"

    # Multipart form data: multipart/form-data
    # Raw data will be parsed as encoded form data
    MULTIPART = "multipart"


@dataclass(slots=True)
class Field:
    name: str | bytes
    value: str | bytes


@dataclass(slots=True)
class PartData:
    """Part for a multipart form"""

    name: str | bytes
    mimetype: str | bytes | None = None
    filename: str | bytes | None = None
    headers: CIMultiDict[str | bytes] = field(default_factory=CIMultiDict)
    body: str | bytes | None = None


BodyItem: TypeAlias = str | bytes | Field | PartData
