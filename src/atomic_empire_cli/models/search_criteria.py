from dataclasses import dataclass


@dataclass
class SearchCriteria():
    name: str
    in_stock: bool
    only_foil: bool
    only_etched: bool
    only_surge: bool
    only_special: bool
    only_normal: bool
