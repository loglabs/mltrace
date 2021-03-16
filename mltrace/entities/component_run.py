from datetime import datetime
from mltrace.entities.base import Base

import pickle
import typing


def get_timestamp() -> int:
    """Returns current timestamp as seconds since epoch."""
    return int(datetime.now().strftime('%s'))


class ComponentRun(Base):
    """Component Run abstraction."""

    def __init__(self, component_name: str, start_timestamp: int, end_timestamp: int, inputs: typing.List[str], outputs: typing.List[str], git_hash: str, code: str, metadata: dict):
        """Set class attributes. Note that timestamps are represented in seconds since epoch."""
        self._component_name = component_name
        self._start_timestamp = start_timestamp
        self._end_timestamp = end_timestamp
        self._inputs = inputs
        self._outputs = outputs
        self._git_hash = git_hash
        self._code = code
        self._metadata = metadata

    @property
    def component_name(self) -> str:
        return self._component_name

    @property
    def inputs(self) -> typing.List[str]:
        return self._inputs

    @property
    def outputs(self) -> typing.List[str]:
        return self._outputs

    @property
    def git_hash(self) -> str:
        return self._git_hash

    @property
    def code(self) -> str:
        return self._code

    @property
    def start_timestamp(self) -> datetime:
        return datetime.utcfromtimestamp(self._start_timestamp)

    def set_start_timestamp(self):
        self._start_timestamp = get_timestamp()

    @property
    def end_timestamp(self) -> datetime:
        return datetime.utcfromtimestamp(self._end_timestamp)

    def set_end_timestamp(self):
        self._end_timestamp = get_timestamp()
