from functools import update_wrapper
from typing import List

import click
import questionary

from aeapi import AtomicEmpireAPI

from models.database import db
from models.card import Card
from models.deck import Deck
from models.crud import save_deck, get_deck, get_decks
from models.remote_card import RemoteCard

from commands import build_in_cmds


@build_in_cmds
@click.group()
def cli():
    pass


@cli.command()
@click.option('--email', '-e', prompt=True, help='Login email for atomicempire.com')
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True, help='Login password for atomicempire.com')
def login(email: str, password: str):
    api = AtomicEmpireAPI()
    api.login(email, password)
    print('Login successfull')


@cli.command()
def get_wishlists():
    response = AtomicEmpireAPI().get_wish_lists()
    print(response)


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
