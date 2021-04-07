from mltrace.db import Store, PointerTypeEnum
from mltrace.entities import Component, ComponentRun, IOPointer

import copy
import functools
import git
import inspect
import logging
import typing
import uuid

CLIENT_DB_URI = 'postgresql://admin:admin@database:5432/sqlalchemy'


def clean_db():
    """Deletes database and reinitializes tables."""
    store = Store(CLIENT_DB_URI, delete_first=True)


def create_component(name: str, description: str, owner: str, tags: typing.List[str] = []):
    """Creates a component entity in the database."""
    store = Store(CLIENT_DB_URI)
    store.create_component(name, description, owner, tags)


def tag_component(component_name: str, tags: typing.List[str]):
    """Adds tags to existing component."""
    store = Store(CLIENT_DB_URI)
    store.add_tags_to_component(component_name, tags)


def backtrace(output_pointer: str):
    """Prints trace for an output id.
        Returns list of tuples (level, ComponentRun) where level is how
        many hops away the node is from the node that produced the output_id."""
    store = Store(CLIENT_DB_URI)
    trace = store.trace(output_pointer)

    # Convert to entities.ComponentRun
    component_runs = []
    for depth, cr in trace:
        inputs = [IOPointer.from_dictionary(iop.__dict__) for iop in cr.inputs]
        outputs = [IOPointer.from_dictionary(
            iop.__dict__) for iop in cr.outputs]
        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update({'inputs': inputs, 'outputs': outputs,
                 'dependencies': dependencies})
        component_runs.append((depth, ComponentRun.from_dictionary(d)))

    return component_runs


def get_history(component_name: str, limit: int = 10) -> typing.List[ComponentRun]:
    """ Returns a list of ComponentRuns that are part of the component's
    history."""
    store = Store(CLIENT_DB_URI)

    history = store.get_history(component_name, limit)

    # Convert to client-facing ComponentRuns
    component_runs = []
    for cr in history:
        inputs = [IOPointer.from_dictionary(
            iop.__dict__).to_dictionary() for iop in cr.inputs]
        outputs = [IOPointer.from_dictionary(
            iop.__dict__).to_dictionary() for iop in cr.outputs]
        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update({'inputs': inputs, 'outputs': outputs,
                 'dependencies': dependencies})
        component_runs.append(ComponentRun.from_dictionary(d))

    return component_runs


def get_components_with_owner(owner: str) -> typing.List[Component]:
    """ Returns a list of all the components associated with the specified
        order."""
    store = Store(CLIENT_DB_URI)
    res = store.get_components_with_owner(owner)

    # Convert to client-facing Components
    components = []
    for c in res:
        tags = [tag.name for tag in c.tags]
        d = copy.deepcopy(c.__dict__)
        d.update({'tags': tags})
        components.append(Component.from_dictionary(d))

    return components


def get_component_information(component_name: str) -> Component:
    """Returns a Component with the name, info, owner, and tags."""
    store = Store(CLIENT_DB_URI)
    c = store.get_component(component_name)
    tags = [tag.name for tag in c.tags]
    d = copy.deepcopy(c.__dict__)
    d.update({'tags': tags})
    return Component.from_dictionary(d)


def get_component_run_information(component_run_id: str) -> ComponentRun:
    """Returns a ComponentRun object."""
    store = Store(CLIENT_DB_URI)
    cr = store.get_component_run(component_run_id)
    inputs = [IOPointer.from_dictionary(
        iop.__dict__).to_dictionary() for iop in cr.inputs]
    outputs = [IOPointer.from_dictionary(
        iop.__dict__).to_dictionary() for iop in cr.outputs]
    dependencies = [dep.component_name for dep in cr.dependencies]
    d = copy.deepcopy(cr.__dict__)
    if cr.code_snapshot:
        d.update({'code_snapshot': str(cr.code_snapshot.decode('utf-8'))})
    d.update({'inputs': inputs, 'outputs': outputs,
              'dependencies': dependencies})
    return ComponentRun.from_dictionary(d)


def get_components_with_tag(tag: str) -> typing.List[Component]:
    """Returns a list of components with the specified tag."""
    store = Store(CLIENT_DB_URI)
    res = store.get_components_with_tag(tag)

    # Convert to client-facing Components
    components = []
    for c in res:
        tags = [tag.name for tag in c.tags]
        d = copy.deepcopy(c.__dict__)
        d.update({'tags': tags})
        components.append(Component.from_dictionary(d))

    return components


def create_random_ids(num_outputs=1) -> typing.List[str]:
    """Returns a list of num_outputs ids."""

    return [uuid.uuid4() for _ in range(num_outputs)]


def log_component_run(component_run: ComponentRun, set_dependencies_from_inputs=True):
    """Takes client-facing ComponentRun object and logs it to the DB."""
    store = Store(CLIENT_DB_URI)

    # Make dictionary object
    component_run_dict = component_run.to_dictionary()

    component_run_sql = store.initialize_empty_component_run(
        component_run.component_name)

    # Add relevant attributes
    component_run_sql.set_start_timestamp(component_run_dict['start_timestamp'])
    component_run_sql.set_end_timestamp(component_run_dict['end_timestamp'])
    component_run_sql.set_git_hash(component_run_dict['git_hash'])
    component_run_sql.set_code_snapshot(component_run_dict['code_snapshot'])

    # Add I/O
    component_run_sql.add_inputs([store.get_io_pointer(
        inp.name, inp.pointer_type) for inp in component_run_dict['inputs']])
    component_run_sql.add_outputs([store.get_io_pointer(
        out.name, out.pointer_type) for out in component_run_dict['outputs']])

    # Add dependencies if there is flag to automatically set
    if set_dependencies_from_inputs:
        store.set_dependencies_from_inputs(component_run_sql)

    # Add dependencies explicitly stored in the component run
    for dependency in component_run_dict['dependencies']:
        cr = store.get_history(dependency, 1)[0]
        component_run_sql.set_upstream(cr)

    store.commit_component_run(component_run_sql)


# Log input strings
# function to apply to outputs to log those

def register(component_name: str, inputs: typing.List[str] = [], outputs: typing.List[str] = [], input_vars: typing.List[str] = [], output_vars: typing.List[str] = [], endpoint: bool = False):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Construct component run object
            store = Store(CLIENT_DB_URI)
            component_run = store.initialize_empty_component_run(component_name)
            component_run.set_start_timestamp()

            # Add input_vars and output_vars as pointers
            input_pointers = [store.get_io_pointer(
                str(kwargs[var])) for var in input_vars]
            output_pointers = [store.get_io_pointer(str(kwargs[var]), PointerTypeEnum.ENDPOINT) for var in output_vars] if endpoint else [
                store.get_io_pointer(str(kwargs[var])) for var in output_vars]

            # Run function
            value = func(*args, **kwargs)

            # Log relevant info
            component_run.set_end_timestamp()
            input_pointers += [store.get_io_pointer(inp) for inp in inputs]
            output_pointers += [store.get_io_pointer(
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
