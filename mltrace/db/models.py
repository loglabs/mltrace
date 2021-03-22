from __future__ import annotations
from datetime import datetime
from mltrace.db.base import Base
from sqlalchemy import Column, String, LargeBinary, Integer, DateTime, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

import enum
import typing


class PointerTypeEnum(enum.Enum):
    DATA_FILE = 1
    MODEL_FILE = 2
    OUTPUT_ID = 3
    UNKNOWN = 4


class Component(Base):
    __tablename__ = 'components'

    name = Column(String, primary_key=True)
    description = Column(String)
    owner = Column(String)
    component_runs = relationship("ComponentRun", cascade='all, delete-orphan')

    def __init__(self, name: str, description: str, owner: str):
        self.name = name
        self.description = description
        self.owner = owner


class IOPointer(Base):
    __tablename__ = 'io_pointers'

    name = Column(String, primary_key=True)
    pointer_type = Column(Enum(PointerTypeEnum))

    def __init__(self, name: str, pointer_type: PointerTypeEnum = None):
        self.name = name
        if pointer_type is not None:
            self.pointer_type = pointer_type

    def set_pointer_type(self, pointer_type: PointerTypeEnum):
        self.pointer_type = pointer_type


component_run_input_association = Table(
    'component_runs_inputs', Base.metadata,
    Column('input_path_name', String, ForeignKey('io_pointers.name')),
    Column('component_run_id', Integer, ForeignKey('component_runs.id'))
)

component_run_output_association = Table(
    'component_runs_outputs', Base.metadata,
    Column('output_path_name', String, ForeignKey('io_pointers.name')),
    Column('component_run_id', Integer, ForeignKey('component_runs.id'))
)

component_run_dependencies = Table(
    'component_run_dependencies', Base.metadata,
    Column('component_run_id', Integer, ForeignKey(
        'component_runs.id'), primary_key=True),
    Column('depends_on_component_run_id', Integer, ForeignKey(
        'component_runs.id'), primary_key=True)
)


class ComponentRun(Base):
    __tablename__ = 'component_runs'

    id = Column(Integer, primary_key=True)
    component_name = Column(String, ForeignKey('components.name'))
    git_hash = Column(String)
    code_snapshot = Column(LargeBinary)
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)
    inputs = relationship(
        "IOPointer", secondary=component_run_input_association, cascade='all, delete-orphan', single_parent=True)
    outputs = relationship(
        "IOPointer", secondary=component_run_output_association, cascade='all, delete-orphan', single_parent=True)
    dependencies = relationship('ComponentRun', secondary=component_run_dependencies, primaryjoin=id == component_run_dependencies.c.component_run_id,
                                secondaryjoin=id == component_run_dependencies.c.depends_on_component_run_id, backref="left_component_run_ids", cascade='all, delete-orphan', single_parent=True)

    def __init__(self, component_name):
        """Initialize ComponentRun, or an instance of a Component's 'run.'"""
        self.component_name = component_name
        self.inputs = []
        self.outputs = []
        self.dependencies = []

    def set_start_timestamp(self, ts: datetime = None):
        """Call this function to set the start timestamp to a specific timestamp or now."""
        self.start_timestamp = ts if ts else datetime.now()

    def set_end_timestamp(self, ts: datetime = None):
        """Call this function to set the end timestamp to a specific timestamp or now."""
        self.end_timestamp = ts if ts else datetime.now()

    def set_code_snapshot(self, code_snapshot: bytes):
        """Code snapshot setter."""
        self.code_snapshot = code_snapshot

    def set_git_hash(self, git_hash: str):
        """Git hash setter."""
        self.git_hash = git_hash

    def add_input(self, input: IOPointer):
        """Add a single input (instance of IOPointer)."""
        self._add_io(input, True)

    def add_inputs(self, inputs: typing.List[IOPointer]):
        """Add a list of inputs (each element should be an instance of IOPointer)."""
        self._add_io(inputs, True)

    def add_output(self, output: IOPointer):
        """"Add a single output (instance of IOPointer)."""
        self._add_io(output, False)

    def add_outputs(self, outputs: typing.List[IOPointer]):
        """Add a list of outputs (each element should be an instance of IOPointer)."""
        self._add_io(outputs, False)

    def _add_io(self, elems: typing.Union[typing.List[IOPointer], IOPointer], input: bool):
        """Helper function to add inputs or outputs."""
        # Elems can be a list or a single IOPointer. Set to a list.
        elems = [elems] if not isinstance(elems, list) else elems
        if input:
            self.inputs += elems
        else:
            self.outputs += elems

    def set_upstream(self, dependencies: typing.Union[typing.List[ComponentRun], ComponentRun]):
        """Set dependencies for this ComponentRun. API similar to Airflow set_upstream."""
        # Dependencies can be a list or a single ComponentRun. Set to a list.
        dependencies = [dependencies] if not isinstance(
            dependencies, list) else dependencies

        self.dependencies += dependencies

    def check_completeness(self) -> dict:
        """Returns a dictionary of success indicator and error messages."""
        status_dict = {'success': True, 'msg': ''}
        if self.start_timestamp is None:
            status_dict['success'] = False
            status_dict['msg'] += f'{self.component_name} ComponentRun has no start timestamp. '
        if self.end_timestamp is None:
            status_dict['success'] = False
            status_dict['msg'] += f'{self.component_name} ComponentRun has no end timestamp. '
        return status_dict
