from typing import List

from sqlalchemy.orm import Session

from .database import db
from .card import Card
from .deck import Deck
from .credentials import Credentials


def get_deck(deck_name: str) -> Deck:
    deck = db.query(Deck).filter(Deck.name == deck_name).first()
    if deck:
        return deck
    else:
        return Deck(name=deck_name)


def get_decks(skip: int = 0, limit: int = 100) -> List[Deck]:
    return db.query(Deck).offset(skip).limit(limit).all()


def save_deck(deck: Deck) -> Deck:
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def delete_deck(deck_id: str):
    db.query(Deck).filter(
        Deck.id == deck_id).delete()
    db.commit()
    return


def create_card(card: Card) -> Card:
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def get_credentials() -> Credentials:
    return db.query(Credentials).first()


def save_credentials(credentials: Credentials) -> Credentials:
    db.add(credentials)
    db.commit()
    db.refresh(credentials)
    return credentials
