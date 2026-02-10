import io
from textwrap import dedent

from requestfile.ast import (
    Argument,
    Command,
    Header,
    Heredoc,
    QuotedValue,
    RawData,
    Requestfile,
    Requestline,
    Symbol,
)
from requestfile.parser import parse_requestfile


def _make_rqf(text):
    return io.StringIO(dedent(text))


def test_parse_single_line():
    stream = _make_rqf("""\
    GET http://example.com
    """)
    req = parse_requestfile(stream)
    assert isinstance(req, Requestfile)
    assert req.requestline == Requestline(
        "GET", Argument(None, Symbol("http://example.com"))
    )
    assert req.preamble == []
    assert req.headers == []
    assert req.content_type is None
    assert req.body == []


def test_parse_simple_request():
    stream = _make_rqf("""\
    POST http://example.com
    Accept: application/json
    Content-type: application/json

    {"id":"hello-world"}
    """)
    req = parse_requestfile(stream)
    assert isinstance(req, Requestfile)
    assert req.requestline == Requestline(
        "POST", Argument(None, Symbol("http://example.com"))
    )
    assert req.preamble == []
    assert req.headers == [
        Header("Accept", "application/json"),
        Header("Content-type", "application/json"),
    ]
    assert req.content_type is None
    assert req.body == [RawData('{"id":"hello-world"}')]


def test_parse_request_with_header_command():
    stream = _make_rqf("""\
    GET http://example.com
    %HEADER: x-example-header "Some value"
    Accept: application/json
    """)
    req = parse_requestfile(stream)
    assert isinstance(req, Requestfile)
    assert req.requestline == Requestline(
        "GET", Argument(None, Symbol("http://example.com"))
    )
    assert req.preamble == []
    assert req.headers == [
        Command(
            "header",
            [
                Argument(None, Symbol("x-example-header")),
                Argument(None, QuotedValue("Some value")),
            ],
        ),
        Header("Accept", "application/json"),
    ]
    assert req.content_type is None
    assert req.body == []


def test_parse_header_command_with_heredoc_value():
    stream = _make_rqf("""\
    GET http://example.com
    %HEADER: x-example-header <<EOF
    Some value
    EOF
    Accept: application/json
    """)
    req = parse_requestfile(stream)
    assert isinstance(req, Requestfile)
    assert req.requestline == Requestline(
        "GET", Argument(None, Symbol("http://example.com"))
    )
    assert req.preamble == []
    assert req.headers == [
        Command(
            "header",
            [
                Argument(None, Symbol("x-example-header")),
                Argument(None, Heredoc("EOF", "Some value")),
            ],
        ),
        Header("Accept", "application/json"),
    ]
    assert req.content_type is None
    assert req.body == []


def test_parse_header_command_with_heredoc_key_and_value():
    stream = _make_rqf("""\
    GET http://example.com
    %HEADER: <<KEY <<VAL
    x-example-header
    KEY
    Some value
    VAL
    Accept: application/json
    """)
    req = parse_requestfile(stream)
    assert isinstance(req, Requestfile)
    assert req.requestline == Requestline(
        "GET", Argument(None, Symbol("http://example.com"))
    )
    assert req.preamble == []
    assert req.headers == [
        Command(
            "header",
            [
                Argument(None, Heredoc("KEY", "x-example-header")),
                Argument(None, Heredoc("VAL", "Some value")),
            ],
        ),
        Header("Accept", "application/json"),
    ]
    assert req.content_type is None
    assert req.body == []
