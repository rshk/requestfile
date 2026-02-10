from requestfile.parser import unquote_value


def test_unquote_plain():
    assert unquote_value('"some string"') == "some string"


def test_unquote_with_double_quotes():
    assert unquote_value('"some \\"string"') == 'some "string'


def test_unquote_with_newline():
    assert unquote_value('"some\\nstring"') == "some\nstring"


def test_unquote_hex():
    assert unquote_value('"\\x41"') == "A"


def test_unquote_unicode_2():
    assert unquote_value('"\\u27F9"') == "\u27f9"


def test_unquote_unicode_4():
    assert unquote_value('"\\U0001F91F"') == "\U0001f91f"
