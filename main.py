import click

from aeapi import AtomicEmpireAPI

from commands import build_in_cmds


@build_in_cmds
@click.group()
def cli():
    pass


@cli.command()
def get_wishlists():
    response = AtomicEmpireAPI().get_wishlists()
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
