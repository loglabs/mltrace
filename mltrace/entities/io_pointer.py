from mltrace.db.models import PointerTypeEnum
from mltrace.entities.base import Base

import json
import pprint


class IOPointer(Base):
    def __init__(
        self, name: str, pointer_type: PointerTypeEnum = PointerTypeEnum.UNKNOWN
    ):
        self._name = name
        self._pointer_type = pointer_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def pointer_type(self) -> PointerTypeEnum:
        return self._pointer_type

    def __repr__(self):
        params = self.to_dictionary()
        params["pointer_type"] = params["pointer_type"].value
        return json.dumps(params)
