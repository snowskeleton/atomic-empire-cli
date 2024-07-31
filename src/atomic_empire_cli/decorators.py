from functools import update_wrapper

import click


def search_options(function):
    @click.pass_context
    @click.option('--name', '-n', required=True, help='Name of the card to search.')
    @click.option('--in-stock', '-i', is_flag=True, help='Only show cards that have a non-zero quantity.')
    @click.option('--foil', is_flag=True, help='Only show foil cards.')
    @click.option('--surge', is_flag=True, help='Only show surge foil cards.')
    @click.option('--etched', is_flag=True, help='Only show etched cards.')
    @click.option('--normal', is_flag=True, help='Only show non-foil, non-etched cards.')
    def wrapper(ctx, *args, **kwargs):
        return ctx.invoke(function, ctx.obj, *args, **kwargs)

    return update_wrapper(wrapper, function)
