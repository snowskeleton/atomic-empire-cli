from __future__ import annotations

from uuid import uuid4
from typing import List

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from . import card

from .database import Base


class Deck(Base):
    __tablename__ = "decks"

    id = Column(String, primary_key=True)
    name = Column(String)
    cards = relationship("Card", back_populates="deck")
    # wishlist = relationship("Wishlist", back_populates="deck", uselist=False)

    def __init__(self, name: str, cards: List[card.Card] = []):
        self.id = str(uuid4())
        self.name = name
        self.cards = cards

    def __repr__(self):
        deckList = ['Name: ' + self.name]
        cardsBought = [
            card for card in self.cards if card.quantity_owned == card.quantity_needed]
        if len(cardsBought) > 0:
            deckList += ['Owned:']
            deckList += [card.__repr__() for card in cardsBought]
        cardsToBuy = [
            card for card in self.cards if card.quantity_owned != card.quantity_needed]
        if len(cardsToBuy) > 0:
            deckList += ['Need More:']
            deckList += [card.__repr__() for card in cardsToBuy]
        return '\n'.join(deckList)
