import click

from ..aeapi import AtomicEmpireAPI
from ..decorators import search_options


@click.group("search")
def cli():
    pass


@cli.command()
@search_options
def search(*args, **options):
    name = options.get('name')
    in_stock = options.get('in_stock')
    foil = options.get('foil')
    surge = options.get('surge')
    etched = options.get('etched')
    normal = options.get('normal')

    cards = AtomicEmpireAPI().search_cards(
        name=name,
        in_stock=in_stock,
        only_foil=foil,
        only_surge=surge,
        only_etched=etched,
        only_normal=normal,
    )
    [print(card) for card in cards]
