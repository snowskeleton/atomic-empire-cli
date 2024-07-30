from functools import update_wrapper
from typing import List

import click
import questionary

from aeapi import AtomicEmpireAPI

from models.database import SessionLocal
from models.card import Card
from models.deck import Deck
from models.crud import save_deck, get_deck, get_decks
from models.remote_card import RemoteCard

db = SessionLocal()


@click.group()
def cli():
    pass


def search_options(function):
    @click.pass_context
    @click.option('--name', '-n', required=True, help='Name of the card to search.')
    @click.option('--in-stock', is_flag=True, help='Only show cards that have a non-zero quantity.')
    @click.option('--foil', is_flag=True, help='Only show foil cards.')
    @click.option('--etched', is_flag=True, help='Only show etched cards.')
    @click.option('--normal', is_flag=True, help='Only show non-foil, non-etched cards.')
    def wrapper(ctx, *args, **kwargs):
        return ctx.invoke(function, ctx.obj, *args, **kwargs)

    return update_wrapper(wrapper, function)


@cli.command()
@search_options
def search(*args, **options):
    name = options.get('name')
    in_stock = options.get('in_stock')
    foil = options.get('foil')
    etched = options.get('etched')
    normal = options.get('normal')

    # api = AtomicEmpireAPI()
    cards = _search(name, in_stock, foil, etched, normal)
    # click.prompt('Pick a card, any card',
    #              type=click.Choice([card for card in cards]))
    [print(card) for card in cards]


@cli.command()
@search_options
def wishlist(*args, **options):
    name = options.get('name')
    in_stock = options.get('in_stock')
    foil = options.get('foil')
    etched = options.get('etched')
    normal = options.get('normal')

    api = AtomicEmpireAPI()
    cards = _search(name, in_stock, foil, etched, normal)

    if not cards:
        print("No cards found with search terms.")
        return

    for idx, card in enumerate(cards):
        print(f"{idx + 1}. {card}")

    # Ask the user to select a card
    card_index = click.prompt('Select a card by number', type=int) - 1
    if card_index < 0 or card_index >= len(cards):
        print("Invalid selection.")
        return

    selected_card = cards[card_index]

    # Ask the user for the quantity
    quantity = click.prompt('Enter quantity', type=int)
    if quantity < 1:
        print("Invalid quantity.")
        return

    # create new wishlist
    wishlist_name = click.prompt('Name your new wishlist', type=str)
    wishlist_id = api.create_wish_list(wishlist_name)['id']

    # Add the selected card to wishlist
    try:
        r = api.add_to_wishlist(selected_card, quantity, wishlist=wishlist_id)
        print(f"Added {quantity} of {selected_card.name} to wishlist.")
        print(r)
    except Exception as e:
        print(f"Failed to add to wishlist: {e}")


def _search(
    name: str,
    in_stock: bool = None,
    foil: bool = None,
    etched: bool = None,
    normal: bool = None,
) -> List[RemoteCard]:
    cards = AtomicEmpireAPI().search_cards(
        name,
        in_stock=in_stock,
        only_foil=foil or etched,
        include_foil=not normal,
    )

    # filters
    if foil:
        cards = [card for card in cards if card.foil]
    if etched:
        cards = [card for card in cards if card.etched]
    if normal:
        cards = [card for card in cards if not card.foil and not card.etched]
    return cards


@cli.command()
@click.option('--email', '-e', prompt=True, help='Login email for atomicempire.com')
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True, help='Login password for atomicempire.com')
def login(email: str, password: str):
    api = AtomicEmpireAPI()
    api.login(email, password)
    print('Login successfull')


@click.group()
def deck():
    pass


@deck.command()
@click.option('--name', '-n', required=True, help='Name your deck.')
def add(name: str):
    # ask user for card names like this:
    # <amount> <Card Name> (<Set>) <Collector Number>
    # The following are acceptable
    # Lightning Bolt
    # 3 Goblin Guide
    # 2 Doomfall (HOU)
    # 2 Doomfall (HOU) 62

    deck = get_deck(db, name)
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
    save_deck(db=db, deck=deck)
    print(deck)


@deck.command()
@click.option('--name', '-n', default=None, help='Print deck by name')
@click.option('--all', '-a', is_flag=True, default=True, help='Print all decks')
@click.option('--names-only', '-o', is_flag=True, default=False, help='Print all deck names')
def list(name: str, all: bool, names_only: bool):
    if name:
        deck = get_deck(db=db, deck_name=name)
        print(deck)
    elif names_only:
        decks = get_decks(db=db)
        [print(deck.name) for deck in decks]
    elif all:
        decks = get_decks(db=db)
        [print(deck) for deck in decks]


@deck.command()
@click.option('--name', '-n', required=True, help='Update purchased-status for cards in a deck by name')
# @click.option('--unowned', '-u', is_flag=True, help='Only show cards not marked as owned')
# @click.option('--owned', '-o', is_flag=True, help='Only show cards currently marked as owned')
# @click.option('--all', '-a', is_flag=True, help='Show all cards in deck')
def update(name: str):
    deck = get_deck(db=db, deck_name=name)

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

    save_deck(db=db, deck=deck)


@deck.command()
@click.option('--name', '-n', required=True, help='Add purchasable cards from named deck to wishlist')
def purchase(name: str):
    deck = get_deck(db=db, deck_name=name)
    wishlist = AtomicEmpireAPI().create_or_get_wishlist('Cards to buy')
    for card in [card for card in deck.cards if card.need_more]:
        kwargs = {
            'name': card.name,
            'in_stock': True,
        }
        if card.foil != None:
            kwargs.update({'foil': card.foil})
        if card.etched != None:
            kwargs.update({'foil': card.etched})
        if card.foil == False and card.etched == False:
            kwargs.update({'normal': True})
        remote_cards = _search(**kwargs)

        if len(remote_cards) == 0:
            print(f'None in stock for: {card.name}')
            continue

        selection = questionary.select(
            "Select the cards you want to add to your wishlist:",
            choices=[questionary.Choice(title="None", value=False)] + [
                questionary.Choice(title=card.__repr__(), value=card) for card in remote_cards
            ],
            show_selected=True,
        ).unsafe_ask()
        if selection:
            AtomicEmpireAPI().add_to_wishlist(
                card=selection,
                quantity=min(card.count_needed, selection.quantity_available),
                wishlist=wishlist,
            )


@cli.command()
def get_wishlists():
    response = AtomicEmpireAPI().get_wish_lists()
    print(response)


cli.add_command(deck)

if __name__ == "__main__":
    cli()

# def main():
#     api = AtomicEmpireAPI()

#     # Login if needed
#     email = ""
#     password = ""
#     login_response = api.login(email, password)
#     print("Logged in:", login_response)

#     # Search for cards
#     query = "Contaminated Aquifer"
#     cards = api.search_cards(query)
#     for card in cards:
#         print(card)

#     # Add the first card to the wishlist
#     if cards:
#         wishlist_id = "42808"
#         add_to_wishlist_response = api.add_to_wishlist(cards[1], quantity=2, wishlist=wishlist_id )
#         print("Added to wishlist:", add_to_wishlist_response)

# if __name__ == "__main__":
#     main()
