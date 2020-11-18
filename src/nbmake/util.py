import sys

import click


def fatal_exit(message: str):
    click.echo(f"Fatal: {message}")
    sys.exit(1)
