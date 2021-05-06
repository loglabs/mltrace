from abc import ABC, abstractmethod


class Base(ABC):
    """The Base class provides methods to save and store attributes as well as
    print them out."""

    # Taken from https://dev.to/mattconway1984/python-creating-instance-properties-2ej0
    def __setattr__(self, attr, value):
        try:
            # Try invoking the descriptor protocol __set__ "manually"
            got_attr = super().__getattribute__(attr)
            got_attr.__set__(self, value)
        except AttributeError:
            # Attribute is not a descriptor, just set it:
            super().__setattr__(attr, value)

    def __getattribute__(self, attr):
        # If the attribute does not exist, super().__getattribute__()
        # will raise an AttributeError
        got_attr = super().__getattribute__(attr)
        try:
            # Try "manually" invoking the descriptor protocol __get__()
            return got_attr.__get__(self, type(self))
        except AttributeError:
            # Attribute is not a descriptor, just return it:
            return got_attr

    def __iter__(self):
        for k in self._properties():
            yield k, self.__getattribute__(k)

    @classmethod
    def _properties(cls):
        return [p for p in cls.__dict__ if isinstance(getattr(cls, p), property)]

    @classmethod
    def from_dictionary(cls, d):
        d = {key: value for key, value in d.items() if key in cls._properties()}
        return cls(**d)

    def to_dictionary(self):
        return {k: self.__getattribute__(k) for k in self._properties()}

    @abstractmethod
    def __repr__(self):
        pass
