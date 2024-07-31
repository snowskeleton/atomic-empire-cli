import click

from aeapi import AtomicEmpireAPI
from decorators import search_options


@click.group("wishlist")
def cli():
    pass


@cli.command()
@search_options
def wishlist(*args, **options):
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
    wishlist = AtomicEmpireAPI().create_or_get_wishlist(wishlist_name)
    # wishlist_id = api.create_wish_list(wishlist_name)['id']

    # Add the selected card to wishlist
    try:
        r = AtomicEmpireAPI().add_to_wishlist(selected_card, quantity, wishlist=wishlist)
        print(f"Added {quantity} of {selected_card.name} to wishlist.")
        print(r)
    except Exception as e:
        print(f"Failed to add to wishlist: {e}")
