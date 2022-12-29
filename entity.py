import dataclasses

from ksuid import ksuid


class FrozenDataClass(type):
    def __new__(cls, *args, **kwargs):
        clazz = super().__new__(cls, *args, **kwargs)
        return dataclasses.dataclass(frozen=True)(clazz)


class ImmutableObject(metaclass=FrozenDataClass):
    pass


class Entity(ImmutableObject):
    id: ksuid
    version: int
