from mltrace.db.models import PointerTypeEnum
from mltrace.entities.base import Base

import json
import typing


class IOPointer(Base):
    def __init__(
        self,
        name: str,
        value: typing.Any = "",
        pointer_type: PointerTypeEnum = PointerTypeEnum.UNKNOWN,
        flag: bool = False,
    ):
        self._name = name
        self._value = value
        self._pointer_type = pointer_type
        self._flag = flag

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> typing.Any:
        return self._value

    @property
    def pointer_type(self) -> PointerTypeEnum:
        return self._pointer_type

    @property
    def flag(self) -> bool:
        return self._flag

    def __repr__(self):
        params = self.to_dictionary()
        del params["value"]
        params["pointer_type"] = params["pointer_type"].value
        return json.dumps(params)
