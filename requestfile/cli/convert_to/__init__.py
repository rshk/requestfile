import click

from .curl import cmd_convert_to_curl


@click.group()
def convert_to():
    pass


convert_to.add_command(cmd_convert_to_curl, name="curl")
