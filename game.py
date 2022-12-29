import dataclasses
from typing import NewType, Dict, List, Tuple, Optional

from _decimal import Decimal
from ksuid import ksuid

from events import GameEvent
from exceptions import GameException
from player import PlayerId, Player

Seat = NewType("Seat", int)


@dataclasses.dataclass(frozen=True)
class Round:
    initial_players: Dict[Seat, PlayerId]
    kicked_players: Tuple[PlayerId] = dataclasses.field(default_factory=tuple)
    finished_players: Tuple[PlayerId] = dataclasses.field(default_factory=tuple)
    current_player: Optional[Player] = dataclasses.field(default=None)
    next_players: Tuple[Player] = dataclasses.field(default_factory=tuple)


class SeatTaken(GameException):
    def __init__(self, seat: Seat):
        super().__init__(f"Seat: {seat} is already taken")
        self.seat = seat


class NoPlayers(GameException):
    def __init__(self):
        super().__init__(f"No players to start new game round")


@dataclasses.dataclass(frozen=True)
class Table:
    number_of_seats: int
    description: str
    rate: int
    bj_multiplayer: Decimal


@dataclasses.dataclass(frozen=True)
class GameTable:
    id: ksuid
    seats: Tuple[Seat]
    taken_seats: Dict[Seat, PlayerId] = dataclasses.field(default_factory=dict)
    current_round: Round = dataclasses.field(default=None)

    def sit(self, seat: Seat, player: Player):
        if seat not in self.taken_seats:
            self.taken_seats[seat] = player.id
        else:
            raise SeatTaken(seat)

    def remove_player(self, player: Player):
        for seat, player_ in self.taken_seats.items():
            if player_.id == player.id:
                self.taken_seats[seat] = None

    def free_seat(self, seat: Seat):
        if seat in self.taken_seats:
            self.taken_seats[seat] = None

    @classmethod
    def of(cls, table: Table):
        return GameTable(ksuid(), tuple(range(1, table.number_of_seats + 1)))

    def start_round(self):
        if not self.taken_seats:
            raise NoPlayers()
        if self.current_round is None:
            return dataclasses.replace(self, current_round=Round(self.taken_seats.copy()))
        else:
            pass


if __name__ == "__main__":
    table = Table(5, "basic table", 1, Decimal("3.2"))
    print(table)
    game_table = GameTable.of(table)
    print(game_table)
    game_table.start_round()
