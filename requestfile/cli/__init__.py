import click
from .parse import cmd_parse
from .send import cmd_send


@click.group()
def main():
    pass


main.add_command(cmd_parse, name="parse")
main.add_command(cmd_send, name="send")
