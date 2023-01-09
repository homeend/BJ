import dataclasses
from typing import NewType, Dict, Tuple, Optional

from _decimal import Decimal
from ksuid import ksuid

from entity import Entity
from exceptions import GameException
from player import PlayerId, Player
from player_hand import PlayerCards

Seat = NewType("Seat", int)


class Round(Entity):
    initial_players: Dict[Seat, PlayerId]
    # kicked_players: Tuple[PlayerId] = dataclasses.field(default_factory=tuple)
    finished_players: Tuple[PlayerId] = dataclasses.field(default_factory=tuple)
    current_player: Optional[Player] = dataclasses.field(default=None)
    awaiting_players: Tuple[PlayerId] = dataclasses.field(default_factory=tuple)
    # players_cards: Dict[PlayerId, PlayerCards]

    @property
    def is_finished(self):
        return self.current_player is None and not self.awaiting_players


class SeatTaken(GameException):
    def __init__(self, seat: Seat):
        super().__init__(f"Seat: {seat} is already taken")
        self.seat = seat


class NoPlayers(GameException):
    def __init__(self):
        super().__init__(f"No players to start new game round")


class RoundInProgress(GameException):
    pass


class Table(Entity):
    number_of_seats: int
    description: str
    rate: int
    bj_multiplayer: Decimal


class GameTable(Entity):
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
        return GameTable(ksuid(), 1, tuple(range(1, table.number_of_seats + 1)))

    def start_round(self):
        if not self.taken_seats:
            raise NoPlayers()
        if self.current_round is None or self.current_round.is_finished:
            return dataclasses.replace(
                self, current_round=Round(self.taken_seats.copy())
            )
        else:
            raise RoundInProgress()
