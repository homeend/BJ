import dataclasses

from player import PlayerId

@dataclasses.dataclass
class DomainEvent:
    pass

@dataclasses.dataclass
class PlayerEvent(DomainEvent):
    playerId: PlayerId

@dataclasses.dataclass
class GameEvent(DomainEvent):
    gameId: "GameId"

@dataclasses.dataclass
class NotEnoughFounds(PlayerEvent):
    playerId: PlayerId
    amount: int

@dataclasses.dataclass
class PlayerBet(PlayerEvent):
    playerId: PlayerId
    amount: int

@dataclasses.dataclass
class PlayerDouble(PlayerEvent):
    playerId: PlayerId
    amount: int

@dataclasses.dataclass
class PlayerHit(PlayerEvent):
    playerId: PlayerId
    card: "Card"

@dataclasses.dataclass
class PlayerStand(PlayerEvent):
    playerId: PlayerId
    hand: "Hand"

@dataclasses.dataclass
class PlayerSplit(PlayerEvent):
    playerId: PlayerId
    card: "Card"
    hand_1: "Hand"
    hand_2: "Hand"

@dataclasses.dataclass
class PlayerGotCard(PlayerEvent):
    playerId: PlayerId
    card: "Card"
    hand: "Hand"