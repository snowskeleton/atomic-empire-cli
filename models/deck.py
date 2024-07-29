from __future__ import annotations

from uuid import uuid4
from typing import List

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

import models.card

from models.database import Base


class Deck(Base):
    __tablename__ = "decks"

    id = Column(String, primary_key=True)
    name = Column(String)
    cards = relationship("Card", back_populates="deck")
    wishlist_id = Column(String, ForeignKey("wishlists.id"))
    wishlist = relationship("Wishlist", back_populates="deck", uselist=False)

    def __init__(self, name: str, cards: List[models.card.Card] = []):
        self.id = str(uuid4())
        self.name = name
        self.cards = cards

    def __repr__(self):
        deckList = [self.name]
        cardsBought = [card for card in self.cards if card.bought]
        if len(cardsBought) > 0:
            deckList += ['Bought:']
            deckList += [card.__repr__() for card in cardsBought]
        cardsToBuy = [card for card in self.cards if not card.bought]
        if len(cardsToBuy) > 0:
            deckList += ['Need to Buy:']
            deckList += [card.__repr__() for card in cardsToBuy]
        return '\n'.join(deckList)
        # return '\n'.join([self.name] + [card.__repr__() for card in self.cards])
