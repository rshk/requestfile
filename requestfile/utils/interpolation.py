import re

RE_VARIABLE = re.compile(
    rb"""
    \$(?:
        \{(.*?)\}
        | ([a-zA-Z0-9_](?:[a-zA-Z0-9_-][a-zA-Z0-9])?)
    )
    """,
    re.VERBOSE,
)


def interpolate_vars(text: str | bytes, data: dict[str, str | bytes]) -> str | bytes:
    """
    Interpolate variables in a template string.

    Replaces $name or ${name} style variables in a str or bytes
    object.

    Does the best effort to return the same text type as the input,
    but with no guarantees.
    """

    if isinstance(text, str):
        result = interpolate_vars(text.encode(), data)

        # Try to decode and return as a string again.
        # This might fail if a variable contained non-utf8 data
        # though, and in that case we just return bytes.
        if isinstance(result, bytes):
            try:
                return result.decode()
            except UnicodeDecodeError:
                pass

        return result

    def _substitution(mo: re.Match) -> bytes:
        assert mo.lastindex is not None
        name = mo.group(mo.lastindex).decode()
        value = data[name]
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode()
        return str(value).encode()

    return RE_VARIABLE.sub(_substitution, text)
