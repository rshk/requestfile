import io
import re
from typing import Iterable, Iterator

from lark import Lark, Transformer

from requestfile.ast import (
    Argument,
    Command,
    Comment,
    Filter,
    Header,
    Heredoc,
    IncludedFile,
    QuotedValue,
    RawData,
    Requestfile,
    Requestline,
    Symbol,
    Variable,
)


def parse_requestfile(
    lines: Iterable[str],
    filename: str | None = None,
) -> Requestfile:
    stream = iter(x.rstrip() for x in lines)
    result = Requestfile(source_filename=filename)
    section = "preamble"

    # Read preamble
    for line in stream:
        if line.startswith("%"):
            command = _parse_requestfile_command(line, stream)
            result.preamble.append(command)

        elif line.startswith("# "):
            comment = Comment(line[2:])
            result.preamble.append(comment)

        elif line.strip() == "":
            # Ignore blank lines in preamble
            result.preamble.append(RawData(""))

        else:
            result.requestline = _parse_requestfile_requestline(line, stream)
            section = "headers"
            break  # End of preamle

    assert section == "headers"

    # Read headers
    for line in stream:
        if line.strip() == "":
            section = "body"
            break  # End of headers
        if line.startswith("%"):
            command = _parse_requestfile_command(line, stream)
            result.headers.append(command)
        elif line.startswith("# "):
            comment = Comment(line[2:])
            result.headers.append(comment)
        else:
            header = _parse_header_line(line)
            result.headers.append(header)

    if section == "body":
        for line in stream:
            if line.strip() == "":
                # Ignore empty lines
                continue
            elif line.startswith("%"):
                command = _parse_requestfile_command(line, stream)
                result.body.append(command)
            elif line.startswith("# "):
                comment = Comment(line[2:])
                result.body.append(comment)
            else:
                raw = RawData(line)
                result.body.append(raw)

    return result


def _parse_requestfile_command(line: str, stream: Iterator[str]) -> Command:
    command = parse_command(line)
    _fill_heredocs_data(command, stream)
    return command


def _parse_requestfile_requestline(line: str, stream: Iterator[str]) -> Requestline:
    requestline = parse_requestline(line)
    _fill_heredocs_data(requestline, stream)
    return requestline


def _parse_header_line(line) -> Header:
    key, val = line.split(":", 1)
    return Header(key.strip(), val.strip())


def _fill_heredocs_data(obj: Command | Requestline, stream: Iterator[str]):
    """
    Load HEREDOC values into a just-loaded object.

    For all HEREDOCs found in an object, consume lines from the stream
    to populate it with data.
    """

    for heredoc in _iter_find_heredocs(obj):
        buf = []
        for x in stream:
            if x == heredoc.marker:
                break
            else:
                buf.append(x)
        heredoc.value = "\n".join(buf)


def _iter_find_heredocs(obj: Command | Requestline) -> Iterable[Heredoc]:
    """
    Iterate all heredocs inside an object.

    Uses depth-first search so they're filled in the order they're
    written in the file.
    """
    match obj:
        case Command(_) as cmd:
            for arg in cmd.arguments:
                if isinstance(arg.value, Heredoc):
                    yield arg.value
        case Requestline(_) as rql:
            if isinstance(rql.url_arg.value, Heredoc):
                yield rql.url_arg.value


line_parser = Lark(
    r"""
    command : "%" SYMBOL ":" (argument)*

    requestline : HTTP_METHOD argument

    argument: [ argname "=" ] argvalue [filters]
    filters: ( "|" filter )*

    ?argname  : SYMBOL

    ?argvalue : symbol
              | quoted
              | heredoc
              | include
              | variable

    heredoc : "<<" symbol

    include : "<" symbol
            | "<" quoted

    variable : "$" SYMBOL

    filter : symbol

    symbol : SYMBOL
    quoted : QUOTED

    SYMBOL : /[a-zA-Z_\/]([a-zA-Z0-9_:\/\.-]*[a-zA-Z0-9_\/])?/
    QUOTED : /".*?(?<!\\)"/
    HTTP_METHOD : /[a-zA-Z]+/

    %import common.WS
    %ignore WS

    """,
    start=["command", "requestline"],
)


class CommandTransformer(Transformer):
    def command(self, items) -> Command:
        [_cmd, *_args] = items
        return Command(_cmd.value.lower(), _args)

    def argument(self, items) -> Argument:
        assert len(items) == 3
        [_name, _value, _filters] = items
        return Argument(_name, _value, filters=_filters or [])

    def symbol(self, items):
        assert len(items) == 1
        [_token] = items
        assert isinstance(_token.value, str)
        return Symbol(_token.value)

    def quoted(self, items):
        assert len(items) == 1
        [_token] = items
        assert isinstance(_token.value, str)
        return QuotedValue(unquote_value(_token.value))

    def heredoc(self, items):
        assert len(items) == 1
        [_token] = items
        assert isinstance(_token.value, str)
        return Heredoc(_token.value)

    def include(self, items):
        assert len(items) == 1
        [value] = items
        assert isinstance(value, (Symbol, QuotedValue))
        return IncludedFile(value)

    def variable(self, items):
        assert len(items) == 1
        [_token] = items
        assert isinstance(_token.value, str)
        return Variable(_token.value)

    def filter(self, items):
        assert len(items) == 1
        [_filter] = items
        assert isinstance(_filter, Symbol)
        return Filter(_filter.value)

    def filters(self, items):
        if items is None:
            return []
        return list(items)

    def requestline(self, items) -> Requestline:
        [method, arg] = items
        return Requestline(method=method.value, url_arg=arg)


QUOTED_CHARS = {
    r"\\": "\\",
    r"\0": "\0",
    r"\a": "\a",
    r"\b": "\b",
    r"\t": "\t",
    r"\n": "\n",
    r"\v": "\v",
    r"\f": "\f",
    r"\r": "\r",
    r"\e": "\x1b",
}

RE_QUOTED = re.compile(
    r"""
        # Hex-encoded sequences
        (?P<qhex>

            # One-byte character, eg: "\x42"
            \\x[0-9a-fA-F]{2}

            # Two-byte unicode characters, eg: "\u27F9"
            |\\u[0-9a-fA-F]{4}

            # Four-byte unicode characters, eg: "\U0001F91F"
            |\\U[0-9a-fA-F]{8}

        )

        # Single-character control codes, like "\n"
        | (?P<qchar>\\.)
    """,
    re.VERBOSE,
)


def unquote_value(text):
    assert text[0] == text[-1] == '"'
    text = text[1:-1]

    def repl_quoted(mo: re.Match):
        value = mo.group()
        match mo.lastgroup:
            case "qhex":
                code = int(value[2:], base=16)
                return chr(code)

            case "qchar":
                try:
                    return QUOTED_CHARS[value]
                except KeyError:
                    # TODO: warning
                    return value[1:]

        raise ValueError(f"Unsupported escape sequence: {mo.group()}")

    return RE_QUOTED.sub(repl_quoted, text)


TO_QUOTED = {_raw: _quot for _quot, _raw in QUOTED_CHARS.items()}


def quote_value(text: str) -> str:
    buf = io.StringIO()
    buf.write('"')

    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            buf.write(TO_QUOTED.get(ch, ch))
        elif code < 256:
            buf.write(r"\x")
            buf.write(format(code, "02x"))
        elif code < 256**2:
            buf.write(r"\u")
            buf.write(format(code, "04x"))
        else:
            assert code < 256**4
            buf.write(r"\U")
            buf.write(format(code, "08x"))

    buf.write('"')
    return buf.getvalue()


def parse_command(text) -> Command:
    tree = line_parser.parse(text, start="command")
    return CommandTransformer().transform(tree)


def parse_requestline(text) -> Requestline:
    tree = line_parser.parse(text, start="requestline")
    return CommandTransformer().transform(tree)
