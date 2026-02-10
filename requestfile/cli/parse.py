import os
import sys

import click

from requestfile.formatting import format_requestfile
from requestfile.parser import parse_requestfile
from requestfile.printing import print_requestfile


@click.command(name="main")
@click.argument("inputfile", type=click.File("r"))
@click.option("--plain", is_flag=True)
def cmd_parse(inputfile, plain):
    filename = inputfile.name
    if filename == "<stdin>":
        filename = None
    else:
        filename = os.path.abspath(filename)

    requestfile = parse_requestfile(inputfile, filename=filename)
    if plain:
        format_requestfile(requestfile, sys.stdout)
    else:
        print_requestfile(requestfile)
