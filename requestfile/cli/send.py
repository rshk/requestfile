import os
import sys

import click
from rich.console import Console
from rich.text import Text

from requestfile.builder import build_request
from requestfile.ext.requests import (
    build_requests_request,
    dump_request_text,
    dump_response,
    dump_response_text,
    send,
)
from requestfile.parser import parse_requestfile
from requestfile.printing import print_requestfile


@click.command(name="send")
@click.argument("inputfile", type=click.File("r"))
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.option("-i", "--show-headers", is_flag=True, default=False)
@click.option("-a", "--arg", "arguments_list", multiple=True)
def cmd_send(inputfile, verbose, show_headers, arguments_list):
    variables = {key: value for key, value in (x.split("=", 1) for x in arguments_list)}

    console = Console(highlight=False, markup=False)

    filename = inputfile.name
    if filename == "<stdin>":
        filename = None
    else:
        filename = os.path.abspath(filename)

    requestfile = parse_requestfile(inputfile, filename=filename)

    if verbose and len(variables):
        console.rule("Variables")
        for key, value in variables.items():
            console.print(
                Text().append(f"{key}:", style="bold").append(" ").append(value)
            )

    if verbose:
        console.rule("Requestfile")
        print_requestfile(requestfile)

    request_info = build_request(requestfile, variables=variables)

    if verbose:
        console.rule("Generic request")
        console.print(request_info)

    request = build_requests_request(request_info)
    if verbose:
        console.rule("Request")
        console.print(dump_request_text(request))

    response = send(request)
    if verbose:
        console.rule("Response")
        console.print(dump_response_text(response))
        console.rule()
    elif show_headers:
        print(dump_response(response))
    else:
        print(response.text)

    sys.exit(0 if response.ok else 1)
