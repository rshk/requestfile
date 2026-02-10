"""
Kinda like formatting, but supports color output.

Slower but fancier.
"""

from typing import TypeAlias

from rich.console import Console
from rich.text import Text
from rich.theme import Theme

from .ast import (
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
    Symbol,
    Variable,
)
from .parser import TO_QUOTED

AstObject: TypeAlias = (
    Requestfile
    | Command
    | Argument
    | Symbol
    | QuotedValue
    | Heredoc
    | IncludedFile
    | Variable
    | Filter
    | Header
    | RawData
)


COLORS = {
    # from https://materialui.co/colors
    "white": "#FAFAFA",
    "black": "#212121",
    "light-grey": "#BDBDBD",
    "grey": "#9E9E9E",
    "dark-grey": "#616161",
    "deep-orange": "#FF5722",
    "green": "#4CAF50",
    "blue": "#2196F3",
    "pink": "#E91E63",
    "teal": "#009688",
    "cyan": "#00BCD4",
    "light-purple": "#BA68C8",
    "purple": "#9C27B0",
    "amber": "#FFC107",
    "light-amber": "#FFE082",
    "green-100": "#C8E6C9",
    "green-900": "#1B5E20",
    "deep-orange-900": "#BF360C",
}
GRUVBOX_THEME = Theme(
    {
        "method": f"bold {COLORS['white']} on {COLORS['deep-orange-900']}",
        "method-get": f"bold {COLORS['white']} on {COLORS['green-900']}",
        "url": "underline " + COLORS["white"],
        "raw": COLORS["light-grey"],
        "keyword": "bold",
        "command": "bold " + COLORS["pink"],
        "symbol": COLORS["white"],
        "quoted": COLORS["green"],
        "quoted-escape": f"bold {COLORS['light-purple']}",
        "heredoc-marker": f"bold {COLORS['amber']}",
        "heredoc-value": COLORS["light-amber"],
        "operator": COLORS["cyan"],
        "variable": COLORS["light-purple"],
        "comment": COLORS["cyan"],
    }
)


def print_requestfile(requestfile: Requestfile):
    console = Console(highlight=False, theme=GRUVBOX_THEME, markup=False)

    for item in requestfile.preamble:
        match item:
            case Command(_):
                _print_command(console, item)
            case Comment(_):
                _print_comment(console, item)
            case RawData(value):
                console.print(value)

    # Sanity checks.
    # These values should have been populated by now
    assert requestfile.requestline is not None

    method = requestfile.requestline.method

    console.print(
        Text()
        .append(
            method,
            style=("method-get" if method in ("GET", "HEAD") else "method"),
        )
        .append(" ")
        .append(_format_argument(requestfile.requestline.url_arg))
    )

    for item in requestfile.headers:
        match item:
            case Header(name, value):
                console.print(
                    Text(style="raw")
                    .append(name + ":", style="keyword")
                    .append(" ")
                    .append(value)
                )
            case Command(_):
                _print_command(console, item)
            case Comment(_):
                _print_comment(console, item)
            case _:
                # Unreachable!
                raise TypeError(f"Unsupported header item: {item}")

    if requestfile.content_type is not None:
        cmd = Command("content-type", [Symbol(requestfile.content_type)])
        _print_command(console, cmd)

    if len(requestfile.body) <= 0:
        return  # We're done here

    console.print()  # Separation line

    for item in requestfile.body:
        match item:
            case Command(_):
                _print_command(console, item)
            case RawData(value):
                console.print(value, style="raw")
            case Comment(_):
                _print_comment(console, item)
            case _:
                # Unreachable!
                raise TypeError(f"Unsupported header item: {item}")


def _format_ast_object(obj: AstObject) -> str | Text:
    match obj:
        case Symbol(value):
            return Text(value, style="symbol")

        case QuotedValue(value):
            return _format_quoted_value(value)

        case Heredoc(marker, _):
            return (
                Text()
                .append("<<", style="operator")
                .append(marker, style="heredoc-marker")
            )

        case IncludedFile(value):
            return (
                Text().append("<", style="operator").append(_format_ast_object(value))
            )

        case Variable(value):
            return Text(f"${value}", style="variable")

        case (
            Requestfile(_)
            | Command(_)
            | Argument(_)
            | Filter(_)
            | Header(_)
            | RawData(_)
        ):
            raise TypeError(f"Unsupported {obj} - use specific function")

        case _:
            # Unreachable!
            raise TypeError(f"Unsupported AST object: {obj}")


def _print_command(console: Console, cmd: Command):
    console.print(Text(f"%{cmd.name}:", style="command"), end="")

    # Write arguments
    for arg in cmd.arguments:
        console.print(" ", end="")
        console.print(_format_argument(arg), end="")
    console.print()

    # Write heredoc values
    for arg in cmd.arguments:
        if isinstance(heredoc := arg.value, Heredoc):
            if heredoc.value is not None:
                console.print(Text(heredoc.value, style="heredoc-value"))
            console.print(Text(heredoc.marker, style="heredoc-marker"))


def _format_argument(arg: Argument) -> str | Text:
    text = Text()

    if arg.name is not None:
        text.append(f"{arg.name}=", style="arg-name")

    text.append(_format_ast_object(arg.value))

    for filter_ in arg.filters:
        text.append("|", style="operator")
        text.append(filter_.name, style="filter-name")

    return text


def _format_quoted_value(text: str) -> str | Text:
    buf = Text(style="quoted")
    buf.append('"')

    for ch in text:
        code = ord(ch)

        if 0x20 <= code <= 0x7E:
            if ch in TO_QUOTED:
                buf.append(TO_QUOTED[ch], style="quoted-escape")
            else:
                buf.append(ch)

        elif code < 256:
            buf.append(f"\\x{code:02x}", style="quoted-escape")
        elif code < 256**2:
            buf.append(f"\\u{code:04x}", style="quoted-escape")
        else:
            buf.append(f"\\U{code:08x}", style="quoted-escape")

    buf.append('"')
    return buf


def _print_comment(console, comment: Comment):
    console.print("#", comment.value, style="comment")
