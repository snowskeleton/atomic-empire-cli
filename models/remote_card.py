from dataclasses import dataclass


@dataclass
class RemoteCard():
    atomic_id: str
    name: str
    set: str
    details: str
    foil: bool
    etched: bool
    surge: bool
    quantity_available: int

    def __repr__(self):
        joinList = [str(self.quantity_available), self.name, self.set]
        if self.surge:
            joinList.append('[S]')
        if self.foil:
            joinList.append('[F]')
        if self.etched:
            joinList.append('[E]')
        return ' '.join(joinList)
