from dataclasses import dataclass


@dataclass
class Wishlist():
    id: str
    name: str

    def __repr__(self):
        return self.name
