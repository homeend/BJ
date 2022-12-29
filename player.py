import dataclasses
from typing import Tuple

from entity import Entity
from player_hand import PlayerCards


class Player(Entity):
    cards: Tuple[PlayerCards, ...]
