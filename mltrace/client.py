from mltrace.db import Store, PointerTypeEnum
from mltrace.entities import Component, ComponentRun, IOPointer

import functools
import git
import inspect
import logging
import typing

DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'


def clean_db():
    """Deletes database and reinitializes tables."""
    store = Store(DB_URI, delete_first=True)


def create_component(name: str, description: str, owner: str):
    """Creates a component entity in the database."""
    store = Store(DB_URI)
    store.create_component(name, description, owner)


def backtrace(output_pointer: str):
    """Prints trace for an output id.
        Returns list of tuples (level, ComponentRun) where level is how
        many hops away the node is from the node that produced the output_id."""
    store = Store(DB_URI)
    trace = store.trace(output_pointer)

    # Convert to entities.ComponentRun
    component_runs = []
    for depth, cr in trace:
        inputs = [IOPointer.from_dictionary(iop.__dict__) for iop in cr.inputs]
        outputs = [IOPointer.from_dictionary(
            iop.__dict__) for iop in cr.outputs]
        d = cr.__dict__
        d.update({'inputs': inputs, 'outputs': outputs})
        component_runs.append((depth, ComponentRun.from_dictionary(d)))

    return component_runs


def get_history(component_name: str, limit: int = 10) -> typing.List[ComponentRun]:
    """ Returns a list of ComponentRuns that are part of the component's
    history."""
    store = Store(DB_URI)
    history = store.get_history(component_name, limit)

    # Convert to client-facing ComponentRuns
    component_runs = []
    for cr in history:
        inputs = [IOPointer.from_dictionary(iop.__dict__) for iop in cr.inputs]
        outputs = [IOPointer.from_dictionary(
            iop.__dict__) for iop in cr.outputs]
        d = cr.__dict__
        d.update({'inputs': inputs, 'outputs': outputs})
        component_runs.append(ComponentRun.from_dictionary(d))

    return component_runs


def get_components_for_owner(owner: str) -> typing.List[Component]:
    """ Returns a list of all the components associated with the specified
        order."""
    store = Store(DB_URI)
    res = store.get_components_for_owner(owner)

    # Convert to client-facing Components
    return [Component.from_dictionary(c.__dict__) for c in res]


def register(component_name: str, inputs: typing.List[str], outputs: typing.List[str], endpoint: bool = False):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Construct component run object
            store = Store(DB_URI)
            component_run = store.initialize_empty_component_run(component_name)
            component_run.set_start_timestamp()

            # Run function
            value = func(*args, **kwargs)

            # Log relevant info
            component_run.set_end_timestamp()
            input_pointers = [store.get_io_pointer(inp) for inp in inputs]
            output_pointers = [store.get_io_pointer(
                out, PointerTypeEnum.ENDPOINT) for out in outputs] if endpoint else [store.get_io_pointer(out) for out in outputs]
            component_run.add_inputs(input_pointers)
            component_run.add_outputs(output_pointers)
            store.set_dependencies_from_inputs(component_run)

            # Add code versions
            try:
                repo = git.Repo(search_parent_directories=True)
                component_run.set_git_hash(str(repo.head.object.hexsha))
            except:
                logging.info('No git repo found.')

            # Add source code if less than 2^16
            func_source_code = inspect.getsource(func)
            if len(func_source_code) < 2**16:
                component_run.set_code_snapshot(
                    bytes(func_source_code, 'ascii'))

            # Commit component run object to the DB
            store.commit_component_run(component_run)

            return value
        return wrapper
    return actual_decorator
