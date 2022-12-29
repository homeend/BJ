import dataclasses

from exceptions import GameException
from player import PlayerId


class ChipsException(GameException):
    pass

class NotEnoughChips(ChipsException):
    def __int__(self, player_chips: "ChipsAmount", other: "ChipsAmount"):
        self.player_chips = player_chips.amount
        self.other = other.amount

@dataclasses.dataclass(frozen=True)
class ChipsAmount:
    amount: int

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Chips amount cannot be negative number")
        if not isinstance(self.amount, int):
            raise ValueError("Chips amount must be integer")

    def __add__(self, other: "ChipsAmount"):
        return ChipsAmount(self.amount + other.amount)

    def __sub__(self, other: "ChipsAmount"):
        if self.amount < other.amount:
            raise NotEnoughChips(self, other)
        return ChipsAmount(self.amount + other.amount)

@dataclasses.dataclass(frozen=True)
class PlayerChips:
    player_id: PlayerId
    amount: ChipsAmount

    def add(self, chips: ChipsAmount):
        return PlayerChips(self.amount + chips)

    def take(self, chips: ChipsAmount):
        return PlayerChips(self.amount - chips)
