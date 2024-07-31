import click

from aeapi import AtomicEmpireAPI
from decorators import search_options
from models.search_criteria import SearchCriteria


@click.command("search")
@search_options
def cli(*args, **options):
    criteria = SearchCriteria(**options)
    cards = AtomicEmpireAPI().search_cards(criteria=criteria)

    [print(card) for card in cards]
