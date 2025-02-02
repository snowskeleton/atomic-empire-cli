from typing import List

import click

from ..aeapi import AtomicEmpireAPI
from ..models.card import Card, pick_a_card
from ..models.crud import save_deck, get_deck, get_decks
from ..models.search_criteria import SearchCriteria


@click.group("deck")
def cli():
    pass


@cli.command()
@click.option('--name', '-n', required=True, help='Name your deck.')
def add(name: str):
    # ask user for card names like this:
    # <amount> <Card Name> (<Set>) <Collector Number>
    # The following are acceptable
    # Lightning Bolt
    # 3 Goblin Guide
    # 2 Doomfall (HOU)
    # 2 Doomfall (HOU) 62

    deck = get_deck(name)
    lines = []
    newlineCount = 0
    print("Paste your deck here and hit <Enter>:")
    while True:
        line = input()
        if not line:
            newlineCount += 1
            if newlineCount > 1:
                break
        if not line:
            continue
        if line not in ['Deck', 'Sideboard', 'About']:
            lines.append(line)
        newlineCount = 0

    deck.cards = [Card(text=line) for line in lines]
    save_deck(deck=deck)
    print(deck)


@cli.command()
@click.option('--name', '-n', default=None, help='Print deck by name')
@click.option('--all', '-a', is_flag=True, default=True, help='Print all decks')
@click.option('--names-only', '-o', is_flag=True, default=False, help='Print all deck names')
def list(name: str, all: bool, names_only: bool):
    if name:
        deck = get_deck(deck_name=name)
        print(deck)
    elif names_only:
        decks = get_decks()
        [print(deck.name) for deck in decks]
    elif all:
        decks = get_decks()
        printableDecks = '\n\n'.join([deck.__repr__() for deck in decks])
        print(printableDecks)


@cli.command()
@click.option('--name', '-n', required=True, help='Update purchased-status for cards in a deck by name')
# @click.option('--unowned', '-u', is_flag=True, help='Only show cards not marked as owned')
# @click.option('--owned', '-o', is_flag=True, help='Only show cards currently marked as owned')
# @click.option('--all', '-a', is_flag=True, help='Show all cards in deck')
def update(name: str):
    deck = get_deck(deck_name=name)

    cardsToBuy: List[Card]
    cardsToBuy = [card for card in deck.cards]

    if len(cardsToBuy) < 1:
        print("No cards in deck")
        return

    print('Enter the quantities of these cards that you own:')
    for card in cardsToBuy:
        quantity = click.prompt(f'{card}', type=int,
                                default=-1, show_default=False)
        if quantity != -1:
            card.quantity_owned = quantity

    save_deck(deck=deck)


@cli.command()
@click.option('--name', '-n', required=True, help='Add purchasable cards from named deck to wishlist')
@click.option('--wishlist', '-w', 'wishlist_name', default='Cards to buy', show_default=False, help='Name of the wishlist to add cards to')
def purchase(name: str, wishlist_name: str):
    deck = get_deck(deck_name=name)
    wishlist = AtomicEmpireAPI().create_or_get_wishlist(wishlist_name)
    for card in [card for card in deck.cards if card.need_more]:
        criteria = SearchCriteria(
            name=card.name,
            in_stock=True,
            only_foil=card.foil,
            only_surge=card.surge,
            only_etched=card.etched,
            only_special=all([
                card.foil == True,
                card.etched == True,
                card.surge == True,
            ]),
            only_normal=all([
                card.foil == False,
                card.etched == False,
                card.surge == False,
            ]),
        )
        remote_cards = AtomicEmpireAPI().search_cards(criteria=criteria)

        if len(remote_cards) == 0:
            print(f'None in stock for: {card.name}')
            continue

        selected_card = pick_a_card(remote_cards)

        if selected_card:
            AtomicEmpireAPI().add_to_wishlist(
                card=selected_card,
                quantity=min(card.count_needed,
                             selected_card.quantity_available),
                wishlist=wishlist,
            )
    wishlist_url = f'https://www.atomicempire.com/WishList/{wishlist.id}'
    print(f'All cards added to wishlist. View wishlist here: {wishlist_url}')
