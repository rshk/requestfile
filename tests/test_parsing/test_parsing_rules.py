from requestfile.ast import (
    Argument,
    Command,
    Filter,
    Heredoc,
    IncludedFile,
    QuotedValue,
    Symbol,
    Variable,
)
from requestfile.parser import CommandTransformer, line_parser


class Test_parse_command:
    class Test_parse_header:
        def test_symbol_symbol(self):
            text = "%HEADER: name value"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, Symbol("value")),
                ],
            )

        def test_symbol_quoted(self):
            text = '%HEADER: name "Some long quoted value"'
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, QuotedValue("Some long quoted value")),
                ],
            )

        def test_symbol_heredoc(self):
            text = "%HEADER: name <<EOF"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, Heredoc("EOF")),
                ],
            )

        def test_symbol_include_symbol(self):
            text = "%HEADER: name </path/to/file.txt"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, IncludedFile(Symbol("/path/to/file.txt"))),
                ],
            )

        def test_symbol_include_quoted(self):
            text = '%HEADER: name <"/path/to/file.txt"'
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, IncludedFile(QuotedValue("/path/to/file.txt"))),
                ],
            )

        def test_symbol_variable(self):
            text = "%HEADER: name $somevar"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, Variable("somevar")),
                ],
            )

        def test_quoted_quoted(self):
            text = '%HEADER: "name" "Some long quoted value"'
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, QuotedValue("name")),
                    Argument(None, QuotedValue("Some long quoted value")),
                ],
            )

        # Filters ----------------------------------------------------

        def test_symbol_symbol_filter(self):
            text = "%HEADER: name value|filter1"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, Symbol("value"), filters=[Filter("filter1")]),
                ],
            )

        def test_symbol_symbol_filter_filter(self):
            text = "%HEADER: name value|filter1|filter2"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(
                        None,
                        Symbol("value"),
                        filters=[Filter("filter1"), Filter("filter2")],
                    ),
                ],
            )

        def test_symbol_filter_symbol_filter(self):
            text = "%HEADER: name|filter1 value|filter2"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(
                        None,
                        Symbol("name"),
                        filters=[Filter("filter1")],
                    ),
                    Argument(
                        None,
                        Symbol("value"),
                        filters=[Filter("filter2")],
                    ),
                ],
            )

        def test_symbol_quoted_filter(self):
            text = '%HEADER: name "Some long quoted value"|filter1'
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(
                        None,
                        QuotedValue("Some long quoted value"),
                        filters=[Filter("filter1")],
                    ),
                ],
            )

        def test_symbol_heredoc_filter(self):
            text = "%HEADER: name <<EOF|filter1"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, Heredoc("EOF"), filters=[Filter("filter1")]),
                ],
            )

        def test_symbol_include_symbol_filter(self):
            text = "%HEADER: name </path/to/file.txt|filter1"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(
                        None,
                        IncludedFile(Symbol("/path/to/file.txt")),
                        filters=[Filter("filter1")],
                    ),
                ],
            )

        def test_symbol_include_quoted_filter(self):
            text = '%HEADER: name <"/path/to/file.txt"|filter1'
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(
                        None,
                        IncludedFile(QuotedValue("/path/to/file.txt")),
                        filters=[Filter("filter1")],
                    ),
                ],
            )

        def test_symbol_variable_filter(self):
            text = "%HEADER: name $somevar|filter1"
            raw_tree = line_parser.parse(text, start="command")
            parsed = CommandTransformer().transform(raw_tree)

            assert parsed == Command(
                "header",
                [
                    Argument(None, Symbol("name")),
                    Argument(None, Variable("somevar"), filters=[Filter("filter1")]),
                ],
            )
