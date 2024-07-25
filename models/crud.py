from typing import List

from sqlalchemy.orm import Session

from models.card import Card
from models.deck import Deck


def get_deck(db: Session, deck_name: str):
    deck = db.query(Deck).filter(Deck.name == deck_name).first()
    if deck:
        return deck
    else:
        return Deck(name=deck_name)
    # return db.query(Deck).filter(Deck.id == deck_id).first()


def delete_deck(db: Session, deck_id: str):
    db.query(Deck).filter(
        Deck.id == deck_id).delete()
    db.commit()
    return


def get_decks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Deck).offset(skip).limit(limit).all()


def create_card(db: Session, card: Card):
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def save_deck(db: Session, deck: Deck):
    # db_deck = db.query(Deck).filter(
    #     Deck.name == deck.name).first()
    # if db_deck:
    #     db_deck.cards = deck.cards
    # else:
    #     db_deck = deck
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


