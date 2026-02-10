import base64
from urllib.parse import quote as urlquote
from urllib.parse import unquote as urlunquote

from requestfile.utils.interpolation import interpolate_vars

from .context import get_builder_context
from requestfile.utils.registry import Registry

FILTERS = Registry()


def get_filter(name):
    return FILTERS.get(name)


@FILTERS.declare("base64")
def filter_base64(text: str | bytes) -> str:
    """Encode string or binary data to a base64 string"""
    if isinstance(text, str):
        text = text.encode()
    return base64.b64encode(text).decode()


@FILTERS.declare("from-base64")
def filter_from_base64(data: str | bytes) -> bytes:
    """Decode a base64 string to binary data"""
    if isinstance(data, str):
        data = data.encode()
    return base64.b64decode(data)


@FILTERS.declare("urlquote")
def filter_urlquote(text: str) -> str:
    """URL-quote a string"""
    return urlquote(text)


@FILTERS.declare("urlunquote")
def filter_urlunquote(text: str) -> str:
    """Unquote a URL-quoted string"""
    return urlunquote(text)


@FILTERS.declare("text")
def filter_text(text: str | bytes) -> str:
    """Decode binary data as unicode text"""
    if isinstance(text, str):
        return text
    return text.decode()


@FILTERS.declare("interpolate")
def filter_interpolate(text: str | bytes) -> str | bytes:
    """Interpolate ${variables} in a chunk of text"""
    ctx = get_builder_context()
    return interpolate_vars(text, ctx.variables)
