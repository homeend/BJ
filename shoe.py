import random
from typing import NewType, List

from cards import Card, Suit, Values


class Shoe:
    def __init__(self, number_of_decks: int = 1, shuffle: bool = False):
        self.cards = [c for _ in range(number_of_decks) for c in deck()]
        if shuffle:
            random.shuffle(self.cards)
        self.used = []
        self._reshuffle_count = 0

    def __iter__(self):
        return iter(self.cards)

    def get_card(self):
        if not self.cards:
            self.reshuffle()
        card = self.cards.pop(0)
        self.used.append(card)
        return card

    def reshuffle(self):
        self.cards = self.used
        self.used = []
        self._reshuffle_count += 1
        random.shuffle(self.cards)

    def reshuffle_count(self):
        return self._reshuffle_count


Deck = NewType("Deck", List[Card])


def deck() -> Deck:
    return [Card(val, suit) for val in _values for suit in Suit]


def _all_values():
    return tuple([getattr(Values, a) for a in dir(Values) if not a.startswith("__")])


_values = tuple(_all_values())
