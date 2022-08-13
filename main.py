import dataclasses
import enum
import random
from typing import List, NewType


class AutoName(enum.Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


class EnumReprMixin(enum.Flag):
    pass

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class PlayerCardsState(EnumReprMixin, enum.Flag):
    PLAYABLE = enum.auto()
    BUSTED = enum.auto()
    SPLITTABLE = enum.auto()
    BJ = enum.auto()


class PlayerAction(EnumReprMixin, AutoName):
    HIT = enum.auto()
    STAND = enum.auto()
    SPLIT = enum.auto()
    DOUBLE = enum.auto()


def main():
    for card in Shoe(2, True):
        print(card)
    assert len(list(Shoe(3))) == 156
    assert len(list(Shoe(3).shuffle())) == 156
    assert len(list(Shoe(2, True))) == 104
    assert set(Shoe()) == set(Shoe(shuffle=True))
    assert len(set(Shoe(shuffle=True))) == 52

    shoe = Shoe()

    player_cards = PlayerCards()
    player_cards.add_card(shoe.get_one())
    player_cards.add_card(shoe.get_one())
    print(player_cards)
    print(player_cards.evaluate())


class Suit(EnumReprMixin, enum.Enum):
    HEART = enum.auto()
    SPADES = enum.auto()
    CLUBS = enum.auto()
    DIAMONDS = enum.auto()


@dataclasses.dataclass(frozen=True)
class Value:
    high: int
    low: int
    name: str

    @staticmethod
    def create(name: str, high: int, low: int = None):
        return Value(high, low or high, name)


class Values:
    ACE = Value.create(name="ace", high=11, low=1)
    TWO = Value.create(name="two", high=2)
    THREE = Value.create(name="three", high=3)
    FOUR = Value.create(name="four", high=4)
    FIVE = Value.create(name="five", high=5)
    SIX = Value.create(name="six", high=6)
    SEVEN = Value.create(name="seven", high=7)
    EIGHT = Value.create(name="eight", high=8)
    NINE = Value.create(name="nine", high=9)
    TEN = Value.create(name="ten", high=10)
    JACK = Value.create(name="jack", high=10)
    QUEEN = Value.create(name="queen", high=10)
    KING = Value.create(name="king", high=10)


def _all_values():
    return tuple([getattr(Values, a) for a in dir(Values) if not a.startswith("__")])


values = tuple(_all_values())


@dataclasses.dataclass(frozen=True)
class Card:
    value: Value
    suit: Suit

    @property
    def high(self):
        return self.value.high

    @property
    def low(self):
        return self.value.low

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value.name.upper()}, suit={self.suit})"


Deck = NewType("Deck", List[Card])


def deck() -> Deck:
    return [Card(val, suit) for val in values for suit in Suit]


class DomainError(Exception):
    pass


class NoMoreCards(DomainError):
    pass


class Shoe:
    def __init__(self, number_of_decks: int = 1, shuffle: bool = False):
        self.cards = [c for _ in range(number_of_decks) for c in deck()]
        if shuffle:
            random.shuffle(self.cards)
        self.used = []

    def __iter__(self):
        return iter(self.cards)

    def shuffle(self):
        return random.sample(self.cards, k=len(self.cards))

    def get_one(self):
        if not self.cards:
            raise NoMoreCards()
        card = self.cards.pop(0)
        self.used.append(card)
        return card


class PlayerCards:
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card):
        self.cards.append(card)
        self.evaluate()

    def high(self):
        return sum(c.high for c in self.cards)

    def low(self):
        return sum(c.low for c in self.cards)

    def evaluate(self) -> PlayerCardsState:
        if self.low() > 21 and self.high() > 21:
            return PlayerCardsState.BUSTED
        return PlayerCardsState.PLAYABLE

    def suits(self):
        return [c.suit for c in self.cards]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cards})"


if __name__ == "__main__":
    main()
