import click

from aeapi import AtomicEmpireAPI
from decorators import search_options
from models.card import pick_a_card
from models.search_criteria import SearchCriteria


@click.command("wishlist")
@search_options
def cli(*args, **options):
    criteria = SearchCriteria(**options)
    cards = AtomicEmpireAPI().search_cards(criteria=criteria)

    if not cards:
        print("No cards found with search terms.")
        return

    selected_card = pick_a_card(cards)
    if selected_card == None:
        print("No card selected")
        return

    # Ask the user for the quantity
    quantity = click.prompt('Enter quantity', type=int)
    if quantity < 1:
        print("Invalid quantity.")
        return

    # create new wishlist
    wishlist_name = click.prompt('Name your new wishlist', type=str)
    wishlist = AtomicEmpireAPI().create_or_get_wishlist(wishlist_name)

    # Add the selected card to wishlist
    try:
        r = AtomicEmpireAPI().add_to_wishlist(selected_card, quantity, wishlist=wishlist)
        print(f"Added {quantity} of {selected_card.name} to wishlist.")
        print(r)
    except Exception as e:
        print(f"Failed to add to wishlist: {e}")
