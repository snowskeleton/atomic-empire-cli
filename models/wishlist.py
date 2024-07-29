from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from models.database import Base


class Wishlist(Base):
    __tablename__ = "wishlists"

    id = Column(String, primary_key=True)
    name = Column(String)
    private = Column(Boolean, default=True)

    deck = relationship("Deck", back_populates="wishlist")

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return ' '.join([str(self.id), self.name])
