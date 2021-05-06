from mltrace.entities.base import Base

import json
import pprint
import typing


class Component(Base):
    """Component abstraction."""

    def __init__(
        self, name: str, description: str, owner: str, tags: typing.List[str] = []
    ):
        """Components should have a name, description, and owner.
        Optionally they will have tags."""
        self._name = name
        self._description = description
        self._owner = owner
        self._tags = tags

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def tags(self) -> typing.List[str]:
        return self._tags

    def __repr__(self):
        params = self.to_dictionary()
        return json.dumps(params)
