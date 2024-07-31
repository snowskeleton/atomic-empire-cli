import re
import json
import os.path

# from time import time
from typing import List, Callable

import click
import requests
from requests import Response
from bs4 import BeautifulSoup

from .models.card import Card, RemoteCard
from .models.wishlist import Wishlist
from .models.search_criteria import SearchCriteria
from .models.crud import get_credentials


class AtomicEmpireAPI:
    authenticated: bool = False

    def __init__(self):
        self.base_url = "https://www.atomicempire.com"
        self.session = requests.Session()
        self.session.trust_env = False
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0"
        }

        # hydrate old cookies
        if os.path.isfile('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookie_dict = json.load(f)

            cookiejar = requests.utils.cookiejar_from_dict(cookie_dict)
            self.session.cookies = cookiejar

            self.session.cookies
            self.authenticated = True

    def __call(self, call: Callable, endpoint: str, **kwargs) -> Response:
        response: Response = call(
            self.base_url + endpoint, **kwargs, headers=self.headers)

        # retry once on expired login
        if response.status_code == 401 and response.reason == 'Authentication Required':
            creds = get_credentials()
            if creds != None:
                print("Login expired.")
                if click.confirm("Try to reauthenticate with saved credentials?", abort=True):
                    self.login(email=creds.email, password=creds.password)
                    return self.__call(call, endpoint, **kwargs)
            else:
                print("Authentication required. Please run:\n\tempire login")
                import sys
                sys.exit()
                click.Abort()


        if response.status_code != 200:
            print(response)
            response.raise_for_status()

        return response

    def _get(self, url: str, **kwargs) -> Response:
        return self.__call(self.session.get, url, **kwargs)

    def _post(self, url: str, **kwargs) -> Response:
        return self.__call(self.session.post, url, **kwargs)

    def login(self, email, password) -> dict:
        login_data = {
            "Email": email,
            "Password": password,
            "X-Requested-With": "XMLHttpRequest"
        }

        response = self._post("/Account/Authenticate", data=login_data)

        # save session cookies to prevent further login
        cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open('cookies.json', 'w') as file:
            json.dump(cookie_dict, file)

        return response.json()

    def search_cards(
        self,
        criteria: SearchCriteria,
    ) -> List[RemoteCard]:
        endpoint = "/Card/List"
        params = {"txt": criteria.name}
        if criteria.in_stock:
            params['instock'] = 1
        if criteria.only_foil:
            # API doesn't differentiate between Foil and Etched, so we have to filter later
            params['foil'] = 1
        if criteria.only_normal:
            params['incfoil'] = 0

        response = self._get(endpoint, params=params)

        cards = hydrate_cards_from_response(response.text)
        # second manual filtering that goes beyond what the API allows
        cards = filter_cards(cards, criteria)

        return cards

    def add_to_wishlist(self, card: RemoteCard, quantity: int, wishlist: Wishlist = None) -> dict:
        endpoint = "/WishList/AddCardToList"
        data = {
            "instanceID": card.atomic_id,
            "quantity": quantity
        }

        if wishlist:
            data["listid"] = wishlist.id

        response = self._post(endpoint, data=data)
        return response.json()

    def get_wishlists(self) -> List[Wishlist]:
        endpoint = "/WishList"
        response = self._post(endpoint)

        soup = BeautifulSoup(response.text, 'html.parser')
        wishlists = []

        wishlist_divs = soup.find_all('div', class_='wishlist-list')
        valid_wishlist_divs = [
            div for div in wishlist_divs if 'mb-3' not in div.get('class', [])]

        for div in valid_wishlist_divs:
            for item in div.find_all('div', class_='list-group-item'):
                if item.find('h6'):
                    list_id = item.get('listid')
                    name = item.find('h6').find('a').get_text(strip=True)
                    wishlists.append(Wishlist(id=list_id, name=name))

        return wishlists

    def create_wishlist(self, name: str) -> Wishlist:
        """Creates a wishlist with the specified name
        Note that this doesn't handle any errors if the name already exists.
        Usually you want to call create_or_get_wishlist() instead

        Args:
            name (str): name of the wishlist to create

        Returns:
            Wishlist: A local representation of the serverside wishlist (without cards)
        """
        endpoint = "/WishList/CreateList"
        data = {
            'listname': name
        }
        response = self._post(endpoint, data=data)
        response_data = response.json()
        return Wishlist(id=response_data['id'], name=name)
        # return response.json()

    def create_or_get_wishlist(self, name) -> Wishlist:
        wishlists = self.get_wishlists()
        for wishlist in wishlists:
            if wishlist.name == name:
                return wishlist
        else:
            return self.create_wishlist(name)

    # only 'type' value I'm aware of is 4. Also referred to as 'itemtype'

    def update_quantity_on_wishlist(self, card: Card, new_quantity: int, wishlist_id: str, type: int = 4) -> dict:
        endpoint = "/UpdateQuantity"
        data = {
            'listid': wishlist_id,
            'id': card.id,
            'type': type,
            'qty': new_quantity
        }
        response = self._post(endpoint, data=data)
        return response.json()

    # Adding to the cart is kinda pointless, because carts aren't saved to an account, but rather to a session.
    # We would have to either walk through the whole buying process, or somehow kick our our session to the
    # browser for the user to finish
    # def add_to_cart(self, card: Card, quantity: int, type: int = 4):
    #     endpoint = "/Cart/AddToCart"

    #     params = {
    #         'itemID': card.id,
    #         'itemType': type,
    #         'quantity': quantity,
    #         '_': time() % 1 # timestamp, round off decimal
    #         }

    #     response = self.get(endpoint, params=params)
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         response.raise_for_status()


def hydrate_cards_from_response(html_text: str) -> List[RemoteCard]:
    soup = BeautifulSoup(html_text, "html.parser")
    cards = []

    for item in soup.find_all("div", class_="item-row"):
        name = item.find("h5").text.strip()
        item_id = item.get("instanceid")

        qty_select = item.find("select", class_="qty")
        qty_strong = item.find(
            "strong", text=lambda t: t and t.startswith("Qty:"))
        if qty_select:
            options = qty_select.find_all("option")
            quantity_available = len(options)
        elif qty_strong:
            quantity_available = int(qty_strong.text.split(":")[1].strip())
        else:
            quantity_available = 0

        details = item.find(
            "p", class_="titledetails").text.strip()
        set_name = re.search(r'from (.+)', details).group(1)

        clean_name = name.replace(
            '[FOIL]', ''
        ).replace(
            '[ETCHED]', ''
        ).replace(
            '(Surge)', ''
        ).strip()

        card = RemoteCard(
            atomic_id=item_id,
            name=clean_name,
            details=details,
            set=set_name,
            quantity_available=quantity_available,
            foil="[FOIL]" in name,
            etched="[ETCHED]" in name,
            surge="(Surge)" in name,
        )
        cards.append(card)

    return cards


def filter_cards(cards: List[Card], criteria: SearchCriteria) -> List[Card]:
    if criteria.only_foil:
        cards = [card for card in cards if card.foil]
    if criteria.only_etched:
        cards = [card for card in cards if card.etched]
    if criteria.only_surge:
        cards = [card for card in cards if card.surge]
    # if criteria.only_special:
    #     cards = [
    #         card for card in cards if any([card.etched, card.foil, card.surge])]
    if criteria.only_normal:
        cards = [
            card for card in cards if not any([card.etched, card.foil, card.surge])]
    return cards
