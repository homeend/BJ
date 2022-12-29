import dataclasses


@dataclasses.dataclass(frozen=True)
class PlayerId:
    value: str

    @staticmethod
    def of(value: str):
        return PlayerId(value)

@dataclasses.dataclass(frozen=True)
class Player:
    id: PlayerId