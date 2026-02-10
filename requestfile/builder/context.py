from contextlib import contextmanager
from dataclasses import dataclass

from requestfile.ast import Requestfile
from contextvars import ContextVar

from .request import Request
from .resource_loader import BaseResourceLoader


@dataclass
class BuilderContext:
    requestfile: Requestfile
    request: Request
    variables: dict[str, str | bytes]
    resource_loader: BaseResourceLoader


_current_builder_context = ContextVar[BuilderContext]("_current_builder_context")


@contextmanager
def set_builder_context(ctx: BuilderContext):
    token = _current_builder_context.set(ctx)
    try:
        yield ctx
    finally:
        _current_builder_context.reset(token)


def get_builder_context() -> BuilderContext:
    return _current_builder_context.get()
