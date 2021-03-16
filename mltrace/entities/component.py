from mltrace.entities.base import Base

import pickle


class Component(Base):
    """Component abstraction."""

    def __init__(self, name: str, description: str, owner: str):
        """Components should have a name, description, and owner."""
        self._name = name
        self._description = description
        self._owner = owner

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def owner(self) -> str:
        return self._owner
