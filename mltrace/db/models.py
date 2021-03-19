from sqlalchemy import Column, String, LargeBinary, Integer, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

from mltrace.db.base import Base


class Component(Base):
    __tablename__ = 'components'

    name = Column(String, primary_key=True)
    description = Column(String)
    owner = Column(String)
    component_runs = relationship("ComponentRun", cascade='all, delete-orphan')

    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner = owner


class IOPointer(Base):
    __tablename__ = 'io_pointers'

    name = Column(String, primary_key=True)

    def __init__(self, name):
        self.name = name


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
        self.component_name = component_name
