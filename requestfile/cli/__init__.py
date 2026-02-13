import click

from .convert_from import convert_from
from .convert_to import convert_to
from .parse import cmd_parse
from .send import cmd_send


@click.group()
def main():
    pass


main.add_command(cmd_parse, name="parse")
main.add_command(cmd_send, name="send")
main.add_command(convert_from, name="from")
main.add_command(convert_to, name="to")
