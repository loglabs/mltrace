from abc import ABC, abstractmethod


class Base(ABC):
    """The Base class provides methods to save and store attributes as well as print them out."""

    def __iter__(self):
        for k in self._properties():
            yield k, self.__getattribute__(k)

    @classmethod
    def _properties(cls):
        return [p for p in cls.__dict__ if isinstance(getattr(cls, p), property)]

    @classmethod
    def from_dictionary(cls, d):
        d = {key: value for key,
             value in d.items() if key in cls._properties()}
        return cls(**d)

    def to_dictionary(self):
        return {k: self.__getattribute__(k) for k in self._properties()}

    @abstractmethod
    def __repr__(self):
        pass
