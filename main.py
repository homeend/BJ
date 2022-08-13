import dataclasses
import enum
import random
from functools import cached_property
from typing import List, NewType, Tuple


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
    START = enum.auto()


class PlayerAction(EnumReprMixin, AutoName):
    HIT = enum.auto()
    STAND = enum.auto()
    SPLIT = enum.auto()
    DOUBLE = enum.auto()


def main():
    # for card in Shoe(2, True):
    #     print(card)
    # assert len(list(Shoe(3))) == 156
    # assert len(list(Shoe(3).shuffle())) == 156
    # assert len(list(Shoe(2, True))) == 104
    # assert set(Shoe()) == set(Shoe(shuffle=True))
    # assert len(set(Shoe(shuffle=True))) == 52

    shoe = Shoe(shuffle=True)

    player_cards = PlayerCards()
    player_cards.add_card(shoe.get_one())
    status = PlayerCardsState.PLAYABLE
    while status != PlayerCardsState.BUSTED:
        player_cards.add_card(shoe.get_one())
        print(player_cards)
        status = player_cards.evaluate()
        print(
            status,
            status & PlayerCardsState.START,
            status & PlayerCardsState.PLAYABLE,
            player_cards.high(),
            player_cards.low(),
        )


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


class CannotModifyHand(DomainError):
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


@dataclasses.dataclass
class CardsEvaluator:
    cards: List[Card]

    def high(self):
        return sum(c.high for c in self.cards)

    def low(self):
        return sum(c.low for c in self.cards)

    def _only_two(self) -> bool:
        return len(self.cards) == 2

    def evaluate(self) -> PlayerCardsState:
        if self._only_two():
            if self.high() == 21:
                return PlayerCardsState.BJ
            elif len(set(self._values())) == 1:
                return PlayerCardsState.SPLITTABLE
            else:
                return PlayerCardsState.START

        elif self.low() > 21 and self.high() > 21:
            return PlayerCardsState.BUSTED

        return PlayerCardsState.PLAYABLE

    def _values(self):
        return [c.value for c in self.cards]

    def value(self):
        high = self.high()
        low = self.low()
        if high == low:
            return high
        return low if high > 21 else high

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cards})"


class PlayerHand:
    def __init__(self, cards: List[Card] = None):
        self._cards = cards or []

    def add_card(
        self, card: Card, other: Card = None, close: bool = False
    ) -> "PlayerHand":
        if other:
            cards = [*self._cards, card, other]
        else:
            cards = [*self._cards, card]

        cards_evaluator = CardsEvaluator(cards)
        player_cards_state = cards_evaluator.evaluate()

        if close:
            if player_cards_state == PlayerCardsState.BUSTED:
                return Busted(cards)
            return Closed(cards)

        match player_cards_state:
            case PlayerCardsState.SPLITTABLE:
                return Splittable(cards)
            case PlayerCardsState.PLAYABLE:
                return PlayerHand(cards)
            case PlayerCardsState.BJ:
                return BlackJack(cards)
            case PlayerCardsState.START:
                return StartHand(cards)
            case PlayerCardsState.BUSTED:
                return Busted(cards)

    @property
    def cards(self) -> List[Card]:
        return self._cards

    @cached_property
    def value(self) -> int:
        return CardsEvaluator(self._cards).value()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cards})"


class Closed(PlayerHand):
    def add_card(self, card: Card, other: Card = None):
        raise CannotModifyHand()


class StartHand(PlayerHand):
    def double_down(self, card: Card) -> Closed:
        return self.add_card(card, close=True)


class Splittable(StartHand):
    def split(self, c1: Card, c2: Card) -> Tuple[StartHand, StartHand]:
        return PlayerHand(self.cards[0]).add_card(c1), PlayerHand(
            self.cards[1]
        ).add_card(c2)


class BlackJack(Closed):
    pass


class Busted(Closed):
    pass


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

    def only_two(self) -> bool:
        return len(self.cards) == 2

    def evaluate(self) -> PlayerCardsState:
        if self.only_two() and self.high() == 21:
            return PlayerCardsState.BJ

        if self.only_two() and len(set(self.values())) == 1:
            return PlayerCardsState.SPLITTABLE

        if self.low() > 21 and self.high() > 21:
            return PlayerCardsState.BUSTED

        if self.only_two():
            return PlayerCardsState.PLAYABLE | PlayerCardsState.START

        return PlayerCardsState.PLAYABLE

    def values(self):
        return [c.value for c in self.cards]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cards})"


if __name__ == "__main__":
    main()
