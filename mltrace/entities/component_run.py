from datetime import datetime
from mltrace.entities.base import Base
from mltrace.entities.io_pointer import IOPointer

import pickle
import pprint
import typing


def get_timestamp() -> int:
    """Returns current timestamp as seconds since epoch."""
    return int(datetime.now().strftime('%s'))


class ComponentRun(Base):
    """Component Run abstraction."""

    def __init__(self, component_name: str, start_timestamp: datetime, end_timestamp: datetime, inputs: typing.List[IOPointer], outputs: typing.List[IOPointer], git_hash: str, code_snapshot: str):
        """Set class attributes. Note that timestamps are represented in seconds since epoch."""
        self._component_name = component_name
        self._start_timestamp = start_timestamp
        self._end_timestamp = end_timestamp
        self._inputs = inputs
        self._outputs = outputs
        self._git_hash = git_hash
        self._code_snapshot = code_snapshot

    @property
    def component_name(self) -> str:
        return self._component_name

    @property
    def inputs(self) -> typing.List[IOPointer]:
        return self._inputs

    @property
    def outputs(self) -> typing.List[IOPointer]:
        return self._outputs

    @property
    def git_hash(self) -> str:
        return self._git_hash

    @property
    def code_snapshot(self) -> str:
        return self._code_snapshot

    @property
    def start_timestamp(self) -> datetime:
        return self._start_timestamp

    @property
    def end_timestamp(self) -> datetime:
        return self._end_timestamp

    def __repr__(self):
        params = self.to_dictionary()
        params['start_timestamp'] = params['start_timestamp'].strftime(
            '%Y-%m-%dT%l:%M:%S%z')
        params['end_timestamp'] = params['end_timestamp'].strftime(
            '%Y-%m-%dT%l:%M:%S%z')
        return pprint.pformat(params)
