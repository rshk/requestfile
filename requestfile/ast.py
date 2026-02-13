from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias


@dataclass(slots=True)
class Requestfile:
    # HTTP method and URL
    requestline: Requestline | None = None

    # Commands specified before the request line
    preamble: list[Command | Comment | RawData] = field(default_factory=list)

    # HTTP header data
    headers: list[Command | Header | Comment] = field(default_factory=list)

    # Requested body content type
    content_type: str | None = None

    # HTTP request body data
    body: list[Command | RawData | Comment] = field(default_factory=list)

    # Path to the file this Requestfile was loaded from.
    # Used to locate files referenced by relative path.
    source_filename: str | None = None


@dataclass(slots=True)
class Requestline:
    method: str
    url_arg: Argument

    @classmethod
    def from_method_and_url(cls, method: str, url: str):
        return cls(method=method, url_arg=Argument(None, QuotedValue(url)))


@dataclass(slots=True)
class Command:
    name: str
    arguments: list


@dataclass(slots=True)
class Argument:
    name: str | None
    value: ArgValue
    filters: list[Filter] = field(default_factory=list)


@dataclass(slots=True)
class Symbol:
    value: str


@dataclass(slots=True)
class QuotedValue:
    value: str


@dataclass(slots=True)
class Heredoc:
    marker: str
    value: str | None = None


@dataclass(slots=True)
class IncludedFile:
    value: Symbol | QuotedValue


@dataclass(slots=True)
class Variable:
    value: str


ArgValue: TypeAlias = Symbol | QuotedValue | Heredoc | IncludedFile | Variable


@dataclass(slots=True)
class Filter:
    name: str


@dataclass(slots=True)
class Header:
    name: str
    value: str


@dataclass(slots=True)
class RawData:
    value: str


@dataclass(slots=True)
class Comment:
    value: str
