from __future__ import annotations

from uuid import uuid4
from typing import List

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

import models.card

from models.database import Base


class Deck(Base):
    __tablename__ = "decks"

    id = Column(String, primary_key=True)
    name = Column(String)
    cards = relationship("Card", back_populates="deck")

    def __init__(self, name: str, cards: List[models.card.Card] = []):
        self.id = str(uuid4())
        self.name = name
        self.cards = cards

    def __repr__(self):
        return '\n'.join([self.name] + [card.__repr__() for card in self.cards])
