import io
from typing import TextIO, TypeAlias

from requestfile.parser import quote_value

from .ast import (
    Argument,
    Command,
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


def format_requestfile(requestfile: Requestfile, stream: TextIO):
    for item in requestfile.preamble:
        _format_command(item, stream)

    stream.write(f"{requestfile.method} {requestfile.url}\n")

    for item in requestfile.headers:
        match item:
            case Header(name, value):
                stream.write(f"{name}: {value}\n")
            case Command(_):
                _format_command(item, stream)
            case _:
                # Unreachable!
                raise TypeError(f"Unsupported header item: {item}")

    if requestfile.content_type is not None:
        cmd = Command("content-type", [Symbol(requestfile.content_type)])
        _format_command(cmd, stream)

    if len(requestfile.body) <= 0:
        return  # We're done here

    stream.write("\n")  # Separation line

    for item in requestfile.body:
        match item:
            case Command(_):
                _format_command(item, stream)
            case RawData(value):
                stream.write(value)
                stream.write("\n")
            case _:
                # Unreachable!
                raise TypeError(f"Unsupported header item: {item}")


def _format_ast_object(obj: AstObject) -> str:
    match obj:
        case Symbol(value):
            return value

        case QuotedValue(value):
            return quote_value(value)

        case Heredoc(marker, _):
            return f"<<{marker}"

        case IncludedFile(value):
            return f"<{_format_ast_object(value)}"

        case Variable(value):
            return f"${value}"

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


def _format_command(cmd: Command, stream: TextIO):
    stream.write(f"%{cmd.name}:")

    # Write arguments
    for arg in cmd.arguments:
        stream.write(" ")
        stream.write(_format_argument(arg))
    stream.write("\n")

    # Write heredoc values
    for arg in cmd.arguments:
        if isinstance(heredoc := arg.value, Heredoc):
            if heredoc.value is not None:
                stream.write(heredoc.value)
                stream.write("\n")
            stream.write(heredoc.marker)
            stream.write("\n")


def _format_argument(arg: Argument) -> str:
    stream = io.StringIO()
    if arg.name is not None:
        stream.write(f"{arg.name}=")
    stream.write(_format_ast_object(arg.value))
    for filter_ in arg.filters:
        stream.write("|")
        stream.write(filter_.name)
    return stream.getvalue()
