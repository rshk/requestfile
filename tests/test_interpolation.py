import pytest
from requestfile.utils.interpolation import interpolate_vars

TEST_CASES = [
    ("", {}, ""),
    (b"", {}, b""),
    ("Foo $bar Baz", {"bar": "BAR"}, "Foo BAR Baz"),
    ("Foo $bar Baz", {"bar": b"BAR"}, "Foo BAR Baz"),
    (b"Foo $bar Baz", {"bar": "BAR"}, b"Foo BAR Baz"),
    (b"Foo $bar Baz", {"bar": b"BAR"}, b"Foo BAR Baz"),
    ("Text $foo and $bar", {"foo": "FOO", "bar": "BAR"}, "Text FOO and BAR"),
    ("Text ${foo} and ${bar}", {"foo": "FOO", "bar": "BAR"}, "Text FOO and BAR"),
    ("Text ${foo bar} text", {"foo bar": "FOOBAR"}, "Text FOOBAR text"),
    ("Text $foo and ${bar}", {"foo": "FOO", "bar": "BAR"}, "Text FOO and BAR"),
]


@pytest.mark.parametrize("text,data,expected", TEST_CASES)
def test_interpolate_vars(text, data, expected):
    assert interpolate_vars(text, data) == expected
