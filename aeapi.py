from time import time
import json
import os.path

from typing import List, Callable

import requests
from requests import Response, post, get
from bs4 import BeautifulSoup

from models.card import Card


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

    def __call(self, call: Callable, endpoint: str, **kwargs) -> dict:
        response: Response = call(
            self.base_url + endpoint, **kwargs, headers=self.headers)
        if response.status_code != 200:
            print(response)
            response.raise_for_status()
        return response

    def _get(self, url: str, **kwargs) -> dict:
        return self.__call(self.session.get, url, **kwargs)

    def _post(self, url: str, **kwargs) -> dict:
        return self.__call(self.session.post, url, **kwargs)

    # def get(self, endpoint, params=None):
    #     url = f"{self.base_url}{endpoint}"
    #     response = self.session.get(
    #         url, headers=self.headers, cookies=self.session.cookies, params=params)
    #     return response

    # def post(self, endpoint, data=None):
    #     url = f"{self.base_url}{endpoint}"
    #     response = self.session.post(
    #         url, headers=self.headers, cookies=self.session.cookies, data=data)
    #     return response

    def login(self, email, password):
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
        query,
        in_stock=False,
        only_foil=False,
        include_foil=True,
    ) -> List[Card]:
        endpoint = "/Card/List"
        params = {"txt": query}
        if in_stock:
            params['instock'] = 1
        if only_foil:
            # API doesn't differentiate between Foil and Etched
            params['foil'] = 1
        if not include_foil:
            params['incfoil'] = 0

        response = self._get(endpoint, params=params)
        # with open("garbage.html", 'w') as file:
        #     file.write(response.text)
        cards = _hydrate_cards_from_response(response.text)

        return cards

    def add_to_wishlist(self, card: Card, quantity: int, wishlist=None):
        endpoint = "/WishList/AddCardToList"
        data = {
            "instanceID": card.id,
            "quantity": quantity
        }

        if wishlist:
            data["listid"] = wishlist

        response = self._post(endpoint, data=data)
        return response.json()

    def get_wish_lists(self):
        endpoint = "/WishList"
        response = self._post(endpoint)
        return response.json()

    def create_wish_list(self, name):
        endpoint = "/WishList/CreateList"
        data = {
            'listname': name
        }
        response = self._post(endpoint, data=data)
        return response.json()

    # only 'type' value I'm aware of is 4. Also referred to as 'itemtype'
    def update_quantity_on_wishlist(self, card: Card, new_quantity: int, wishlist_id: str, type: int = 4):
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


def _hydrate_cards_from_response(html_text: str) -> List[Card]:
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

        # details = item.find(
        #     "p", class_="titledetails").text.strip()

        card = Card(
            id=item_id,
            name=name,
            # details=details,
            quantity=quantity_available,
            foil="[FOIL]" in name,
            etched="[ETCHED]" in name
        )
        cards.append(card)

    return cards
