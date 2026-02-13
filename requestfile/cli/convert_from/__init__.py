import click
from .curl import cmd_convert_from_curl


@click.group()
def convert_from():
    pass


convert_from.add_command(cmd_convert_from_curl, name="curl")
