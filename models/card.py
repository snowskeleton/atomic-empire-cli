from __future__ import annotations

import re
import uuid

from dataclasses import dataclass

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import deck

from .database import Base


@dataclass
class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True)
    name = Column(String)
    set = Column(String)
    foil = Column(Boolean)
    etched = Column(Boolean)
    quantity_owned = Column(Integer)
    quantity_needed = Column(Integer)
    collector_number = Column(Integer)

    deck_id = Column(String, ForeignKey("decks.id"))
    deck = relationship("Deck", back_populates="cards")

    @property
    def need_more(self) -> bool:
        return self.quantity_needed > self.quantity_owned

    @property
    def count_needed(self) -> int:
        return self.quantity_needed - self.quantity_owned

    def __init__(self, deck: deck.Deck = None, text: str = None, foil: bool = None, etched: bool = None, card: Card = None):
        """create object from text input, with format
        <amount> <Card Name> (<Set>) <Collector Number>
        where "amount", "set", and "collector number" are optional.

        Args:
            deck (Deck): parent deck
            text (str): <amount> <Card Name> (<Set>) <Collector Number>
        """

        # Initialize defaults
        self.id = str(uuid.uuid4())
        self.deck = deck
        self.quantity_needed = 1
        self.quantity_owned = 0
        self.name = ""
        self.set = ""
        self.collector_number = None
        self.foil = foil
        self.etched = etched
        # self.bought = False

        # Define a regex pattern to match the input text

        if card:
            self.quantity_needed = card.quantity_needed
            self.quantity_owned = card.quantity_owned
            self.name = card.name
            self.set = card.set
            self.collector_number = card.collector_number
        elif text:
            pattern = r"(?:(\d+)\s+)?(.+?)(?:\s+\(([^)]+)\))?(?:\s+(\d+))?$"
            match = re.match(pattern, text)
            self.quantity_needed = int(match.group(1)) if match.group(1) else 1
            self.name = match.group(2)
            self.set = match.group(3)
            self.collector_number = match.group(4)
        else:
            raise("No data provided to instantiate card")

    def __repr__(self):
        return ' '.join([f'{self.quantity_owned}/{self.quantity_needed}', self.name])
