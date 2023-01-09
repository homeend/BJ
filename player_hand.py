import dataclasses
import enum
from functools import cached_property
from typing import List, Union, Tuple

from ksuid import ksuid

from base import DomainError
from cards import Card, Values


class HandCardsState(enum.Enum):
    PLAYABLE = enum.auto()
    BUSTED = enum.auto()
    SPLITTABLE = enum.auto()
    BJ = enum.auto()
    START = enum.auto()


class CardsAction(enum.Enum):
    HIT = enum.auto()
    STAND = enum.auto()
    SPLIT = enum.auto()
    DOUBLE = enum.auto()


class CannotModifyHand(DomainError):
    pass


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

    def evaluate(self) -> HandCardsState:
        high = CardUtils.high(self.cards)
        low = CardUtils.low(self.cards)
        if len(self.cards) == 2:
            if high == 21:
                return HandCardsState.BJ
            elif len(set(self._values())) == 1:
                return HandCardsState.SPLITTABLE
            else:
                return HandCardsState.START

        elif low > 21 and high > 21:
            return HandCardsState.BUSTED

        return HandCardsState.PLAYABLE

    def _values(self):
        return [c.value for c in self.cards]


class PlayerCards:
    def __init__(self, card_or_cards: Union[Card, List[Card]] = None):
        self.id = ksuid()

        if isinstance(card_or_cards, Card):
            self._cards = [card_or_cards]
        else:
            self._cards = card_or_cards or []

        if len(self._cards) > 1:
            self.value = CardUtils.value(self._cards)

    def hit(self, card: Card, close: bool = False) -> "PlayerCards":
        cards = [*self._cards, card]
        player_cards_state = CardsEvaluator(cards).evaluate()

        if close:
            if player_cards_state == HandCardsState.BUSTED:
                return Busted(cards)
            return Closed(cards)

        match player_cards_state:
            case HandCardsState.SPLITTABLE:
                return Splittable(cards)
            case HandCardsState.PLAYABLE:
                return PlayerCards(cards)
            case HandCardsState.BJ:
                return BlackJack(cards)
            case HandCardsState.START:
                return StartHand(cards)
            case HandCardsState.BUSTED:
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


class Closed(PlayerCards):
    def hit(self, card: Card):
        raise CannotModifyHand()


class StartHand(PlayerCards):
    def double_down(self, card: Card) -> Closed:
        return self.hit(card, close=True)


class Splittable(StartHand):
    def split(self, c1: Card, c2: Card) -> Tuple[StartHand, StartHand]:
        return PlayerCards(self.cards[0]).hit(c1), PlayerCards(self.cards[1]).hit(c2)


class BlackJack(Closed):
    pass


class Busted(Closed):
    pass
