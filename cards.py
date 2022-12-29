import dataclasses
import enum


class Suit(enum.Enum):
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
