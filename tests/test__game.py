import dataclasses

import pytest
from _decimal import Decimal
from ksuid import ksuid

from game import Table, GameTable, NoPlayers, SeatTaken


@pytest.fixture
def basic_table() -> Table:
    return Table(5, "basic table", 1, Decimal("3.2"))


def test__game__start_round__exception(basic_table: Table):
    with pytest.raises(NoPlayers):
        GameTable.of(basic_table).start_round()


def test__game__start_round__exception__sit_taken(basic_table: Table):
    @dataclasses.dataclass
    class P:
        id: str = dataclasses.field(default_factory=ksuid)
    game_table = GameTable.of(basic_table)
    first_seat = game_table.seats[0]
    game_table.sit(first_seat, P())
    with pytest.raises(SeatTaken):
        game_table.sit(first_seat, P())
