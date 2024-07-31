import click

from . import (
    cmd_deck,
    cmd_search,
    cmd_wishlist,
)

cli_commands = [
    cmd_deck.cli,
    cmd_search.cli,
    cmd_wishlist.cli,
]


def build_in_cmds(func=None):
    """
    A decorator to register build-in CLI commands to an instance of
    `click.Group()`.

    Returns
    -------
    click.Group()
    """
    def decorator(group):
        if not isinstance(group, click.Group):
            raise TypeError(
                "Plugins can only be attached to an instance of "
                "click.Group()"
            )

        for cmd in cli_commands:
            group.add_command(cmd)

        return group

    if callable(func):
        return decorator(func)

    return decorator
