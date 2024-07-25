
def test_hydrate_cards_from_response():
    from aeapi import _hydrate_cards_from_response
    with open('tests/sample_data/lightning_bolt_list.html', 'r') as file:
        cards = _hydrate_cards_from_response(file.read())
        for card in cards:
            print(card)
