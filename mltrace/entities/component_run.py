# from __future__ import annotations
from datetime import datetime
from mltrace.db import PointerTypeEnum
from mltrace.db.utils import _map_extension_to_enum
from mltrace.entities.base import Base
from mltrace.entities.io_pointer import IOPointer

import json
import pickle
import pprint
import typing


def get_timestamp() -> int:
    """Returns current timestamp as seconds since epoch."""
    return int(datetime.utcnow().strftime("%s"))


class ComponentRun(Base):
    """Component Run abstraction."""

    def __init__(
        self,
        component_name: str,
        start_timestamp: datetime = None,
        end_timestamp: datetime = None,
        inputs: typing.List[IOPointer] = [],
        outputs: typing.List[IOPointer] = [],
        git_hash: str = None,
        code_snapshot: str = None,
        id: str = None,
        dependencies: typing.List[str] = [],
    ):
        """Set class attributes. Note that timestamps are represented in
        seconds since epoch."""
        self._component_name = component_name
        self._start_timestamp = start_timestamp
        self._end_timestamp = end_timestamp
        self._inputs = inputs
        self._outputs = outputs
        self._git_hash = git_hash
        self._code_snapshot = (
            code_snapshot.decode("utf-8")
            if isinstance(code_snapshot, (bytes, bytearray))
            else code_snapshot
        )
        self._id = id
        self._dependencies = dependencies

    @property
    def component_name(self) -> str:
        return self._component_name

    @property
    def inputs(self) -> typing.List[IOPointer]:
        return self._inputs

    @inputs.setter
    def inputs(self, inputs: typing.List[IOPointer]):
        self._inputs = inputs

    @inputs.deleter
    def inputs(self):
        del self._inputs

    @property
    def outputs(self) -> typing.List[IOPointer]:
        return self._outputs

    @outputs.setter
    def outputs(self, outputs: typing.List[IOPointer]):
        self._outputs = outputs

    @outputs.deleter
    def outputs(self):
        del self._outputs

    @property
    def git_hash(self) -> str:
        return self._git_hash

    @git_hash.setter
    def git_hash(self, new_hash: str):
        self._git_hash = new_hash

    @property
    def code_snapshot(self) -> str:
        return self._code_snapshot

    @code_snapshot.setter
    def code_snapshot(self, new_snapshot: str):
        self._code_snapshot = new_snapshot

    @property
    def start_timestamp(self) -> datetime:
        return self._start_timestamp

    @property
    def end_timestamp(self) -> datetime:
        return self._end_timestamp

    @property
    def dependencies(self) -> typing.List[str]:
        return self._dependencies

    @property
    def id(self) -> str:
        return self._id

    def set_start_timestamp(self, ts: datetime = None):
        if ts is None:
            ts = datetime.utcnow()

        if not isinstance(ts, datetime):
            raise TypeError("Timestamp must be of type datetime.")

        self._start_timestamp = ts

    def set_end_timestamp(self, ts: datetime = None):
        if ts is None:
            ts = datetime.utcnow()

        if not isinstance(ts, datetime):
            raise TypeError("Timestamp must be of type datetime.")

        self._end_timestamp = ts

    def add_input(
        self, inp: typing.Union[str, IOPointer], pointer_type: PointerTypeEnum = None
    ):
        """Add a single input (instance of IOPointer)."""
        if isinstance(inp, IOPointer):
            self._add_io(inp, True)
            return

        if pointer_type is None:
            pointer_type = _map_extension_to_enum(inp)
        self._add_io(IOPointer(inp, pointer_type), True)

    def add_inputs(self, inputs: typing.List[typing.Union[str, IOPointer]]):
        """Add a list of inputs (each element should be an instance of
        IOPointer)."""
        for inp in inputs:
            if isinstance(inp, str):
                self.add_input(inp)
            else:
                self._add_io(inp, True)

    def add_output(
        self, out: typing.Union[str, IOPointer], pointer_type: PointerTypeEnum = None
    ):
        """ "Add a single output (instance of IOPointer)."""
        if isinstance(out, IOPointer):
            self._add_io(out, False)
            return

        if pointer_type is None:
            pointer_type = _map_extension_to_enum(out)
        self._add_io(IOPointer(out, pointer_type), False)

    def add_outputs(self, outputs: typing.List[typing.Union[str, IOPointer]]):
        """Add a list of outputs (each element should be an instance of IOPointer)."""
        for out in outputs:
            if isinstance(out, str):
                self.add_output(out)
            else:
                self._add_io(out, False)

    def _add_io(
        self, elems: typing.Union[typing.List[IOPointer], IOPointer], input: bool
    ):
        """Helper function to add inputs or outputs."""
        # Elems can be a list or a single IOPointer. Set to a list.
        elems = [elems] if not isinstance(elems, list) else elems
        if input:
            self.inputs = list(set(self.inputs + elems))
        else:
            self.outputs = list(set(self.outputs + elems))

    def set_upstream(self, dependencies: typing.Union[str, typing.List[str]]):
        """Set dependencies for this ComponentRun. API similar to Airflow
        set_upstream. It will grab the most recent run for the dependency
        name."""
        # Dependencies can be a list or a single string. Set to a list.
        dependencies = (
            [dependencies] if not isinstance(dependencies, list) else dependencies
        )

        self._dependencies = self._dependencies + dependencies
        self._dependencies = list(set(self._dependencies))

    def __repr__(self):
        params = self.to_dictionary()
        if params["start_timestamp"] is not None:
            params["start_timestamp"] = params["start_timestamp"].strftime(
                "%Y-%m-%d %l:%M:%S%z"
            )
        if params["end_timestamp"] is not None:
            params["end_timestamp"] = params["end_timestamp"].strftime(
                "%Y-%m-%d %l:%M:%S%z"
            )
        return json.dumps(params)
