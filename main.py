import dataclasses
import enum
import random
from functools import cached_property
from typing import List, NewType, Tuple, Union


class AutoName(enum.Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


class EnumReprMixin(enum.Flag):
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


class CardUtils:
    @staticmethod
    def high(cards: List[Card]):
        return sum(c.high for c in cards)

    @staticmethod
    def low(cards: List[Card]):
        return sum(c.low for c in cards)

    @staticmethod
    def value(cards: List[Card]):
        high = CardUtils.high(cards)
        low = CardUtils.low(cards)
        if high == low:
            return high
        return low if high > 21 else high


@dataclasses.dataclass
class CardsEvaluator:
    cards: List[Card]

    def evaluate(self) -> PlayerCardsState:
        high = CardUtils.high(self.cards)
        low = CardUtils.low(self.cards)
        if len(self.cards) == 2:
            if high == 21:
                return PlayerCardsState.BJ
            elif len(set(self._values())) == 1:
                return PlayerCardsState.SPLITTABLE
            else:
                return PlayerCardsState.START

        elif low > 21 and high > 21:
            return PlayerCardsState.BUSTED

        return PlayerCardsState.PLAYABLE

    def _values(self):
        return [c.value for c in self.cards]


class PlayerHand:
    def __init__(self, card_or_cards: Union[Card, List[Card]] = None):
        if isinstance(card_or_cards, Card):
            self._cards = [card_or_cards]
        else:
            self._cards = card_or_cards or []

        if len(self._cards) > 1:
            self.value = CardUtils.value(self._cards)

    def hit(self, card: Card, close: bool = False) -> "PlayerHand":
        cards = [*self._cards, card]
        player_cards_state = CardsEvaluator(cards).evaluate()

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

    def stand(self):
        return Closed(self._cards)

    @property
    def cards(self) -> List[Card]:
        return self._cards

    def value(self) -> int:
        return self.value

    @cached_property
    def is_hard(self) -> int:
        return Values.ACE not in {c.value for c in self.cards}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cards})"


class Closed(PlayerHand):
    def hit(self, card: Card):
        raise CannotModifyHand()


class StartHand(PlayerHand):
    def double_down(self, card: Card) -> Closed:
        return self.hit(card, close=True)


class Splittable(StartHand):
    def split(self, c1: Card, c2: Card) -> Tuple[StartHand, StartHand]:
        return PlayerHand(self.cards[0]).hit(c1), PlayerHand(self.cards[1]).hit(c2)


class BlackJack(Closed):
    pass


class Busted(Closed):
    pass


def main():
    # for card in Shoe(2, True):
    #     print(card)
    # assert len(list(Shoe(3))) == 156
    # assert len(list(Shoe(3).shuffle())) == 156
    # assert len(list(Shoe(2, True))) == 104
    # assert set(Shoe()) == set(Shoe(shuffle=True))
    # assert len(set(Shoe(shuffle=True))) == 52

    shoe = Shoe(shuffle=True)

    played = []
    in_play = []

    while shoe.reshuffle_count() == 0:
        print("\u2500" * 100)
        player_cards = PlayerHand(shoe.get_card())
        player_cards = player_cards.hit(shoe.get_card())
        print(player_cards, player_cards.value)

        in_play.append(player_cards)

        while in_play:
            player_hand = in_play.pop(0)
            if isinstance(player_hand, Splittable):
                print("splitting", player_hand.cards[0].value.name)
                h1, h2 = player_hand.split(shoe.get_card(), shoe.get_card())
                print("new cards", h1)
                print("new cards", h2)
                in_play.append(h1)
                in_play.append(h2)
                continue

            while not isinstance(player_hand, Closed):
                if (
                    isinstance(player_hand, StartHand)
                    and player_hand.is_hard
                    and player_hand.value < 10
                ):
                    player_hand = player_hand.double_down(shoe.get_card())
                    print(
                        "double down",
                        player_hand,
                        player_hand.value,
                    )
                elif player_hand.value >= 19:
                    player_hand = player_hand.stand()
                else:
                    player_hand = player_hand.hit(shoe.get_card())
                    print(
                        "hit",
                        player_hand,
                        player_hand.value,
                    )
            played.append(player_hand)

    print("\u2500"*100)
    print("\u2500"*100)

    for hand in played:
        print("played", hand, hand.value)


if __name__ == "__main__":
    main()
