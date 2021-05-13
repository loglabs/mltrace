from datetime import datetime
from mltrace.db import Store, PointerTypeEnum
from mltrace.entities import Component, ComponentRun, IOPointer

import copy
import functools
import git
import inspect
import logging
import os
import sys
import typing
import uuid


def _set_address_helper(old_uri: str, address: str):
    first = old_uri.split("@")[0]
    last = old_uri.split("@")[1].split(":")[1]
    return first + "@" + address + ":" + last


_db_uri = os.environ.get("DB_URI")
if _db_uri is None:
    _db_uri = "postgresql://admin:admin@localhost:5432/sqlalchemy"
    if os.environ.get("DB_SERVER"):
        _db_uri = _set_address_helper(_db_uri, os.environ.get("DB_SERVER"))
    else:
        logging.warning(
            f"Please set DB_URI or DB_SERVER as an environment variable. Otherwise, DB_URI is set to {_db_uri}."
        )

# ----------------------- Database management functions ---------------------- #


def set_db_uri(uri: str):
    global _db_uri
    _db_uri = uri


def get_db_uri() -> str:
    global _db_uri
    return _db_uri


def set_address(address: str):
    global _db_uri
    _db_uri = _set_address_helper(_db_uri, address)


def clean_db():
    """Deletes database and reinitializes tables."""
    store = Store(_db_uri, delete_first=True)


# ---------------------------- Creation functions ---------------------------- #


def create_component(
    name: str, description: str, owner: str, tags: typing.List[str] = []
):
    """Creates a component entity in the database."""
    store = Store(_db_uri)
    store.create_component(name, description, owner, tags)


def tag_component(component_name: str, tags: typing.List[str]):
    """Adds tags to existing component."""
    store = Store(_db_uri)
    store.add_tags_to_component(component_name, tags)


def log_component_run(component_run: ComponentRun, set_dependencies_from_inputs=True):
    """Takes client-facing ComponentRun object and logs it to the DB."""
    store = Store(_db_uri)

    # Make dictionary object
    component_run_dict = component_run.to_dictionary()

    component_run_sql = store.initialize_empty_component_run(
        component_run.component_name
    )

    # Add relevant attributes
    if component_run_dict["start_timestamp"]:
        component_run_sql.set_start_timestamp(component_run_dict["start_timestamp"])

    if component_run_dict["end_timestamp"]:
        component_run_sql.set_end_timestamp(component_run_dict["end_timestamp"])

    component_run_sql.set_git_hash(component_run_dict["git_hash"])
    component_run_sql.set_code_snapshot(component_run_dict["code_snapshot"])

    # Add I/O
    component_run_sql.add_inputs(
        [
            store.get_io_pointer(inp.name, inp.pointer_type)
            for inp in component_run_dict["inputs"]
        ]
    )
    component_run_sql.add_outputs(
        [
            store.get_io_pointer(out.name, out.pointer_type)
            for out in component_run_dict["outputs"]
        ]
    )

    # Add dependencies if there is flag to automatically set
    if set_dependencies_from_inputs:
        store.set_dependencies_from_inputs(component_run_sql)

    # Add dependencies explicitly stored in the component run
    for dependency in component_run_dict["dependencies"]:
        cr = store.get_history(dependency, 1)[0]
        component_run_sql.set_upstream(cr)

    store.commit_component_run(component_run_sql)


def create_random_ids(num_outputs=1) -> typing.List[str]:
    """Returns a list of num_outputs ids that a client can use to tag outputs."""

    return [str(uuid.uuid4()) for _ in range(num_outputs)]


# Log input strings
# function to apply to outputs to log those


def register(
    component_name: str,
    inputs: typing.List[str] = [],
    outputs: typing.List[str] = [],
    input_vars: typing.List[str] = [],
    output_vars: typing.List[str] = [],
    endpoint: bool = False,
):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function information
            filename = inspect.getfile(func)
            function_name = func.__name__

            # Construct component run object
            store = Store(_db_uri)
            component_run = store.initialize_empty_component_run(component_name)
            component_run.set_start_timestamp()

            # Define trace helper
            def trace_helper(frame, event, arg):
                if event != "return":
                    return

                logging.info(f"Inspecting {frame.f_code.co_filename}")
                input_pointers = []
                output_pointers = []
                local_vars = frame.f_locals
                # Add input_vars and output_vars as pointers
                for var in input_vars:
                    if var not in local_vars:
                        logging.debug(f"Variable {var} not in current stack frame.")
                        continue
                    val = local_vars[var]
                    if val == None:
                        logging.debug(f"Variable {var} has value {val}.")
                        continue
                    if isinstance(val, list):
                        input_pointers += store.get_io_pointers(val)
                    else:
                        input_pointers.append(store.get_io_pointer(str(val)))
                for var in output_vars:
                    if var not in local_vars:
                        logging.debug(f"Variable {var} not in current stack frame.")
                        continue
                    val = local_vars[var]
                    if val == None:
                        logging.debug(f"Variable {var} has value {val}.")
                        continue
                    if isinstance(val, list):
                        output_pointers += (
                            store.get_io_pointers(val, PointerTypeEnum.ENDPOINT)
                            if endpoint
                            else store.get_io_pointers(val)
                        )
                    else:
                        output_pointers += (
                            [store.get_io_pointer(str(val), PointerTypeEnum.ENDPOINT)]
                            if endpoint
                            else [store.get_io_pointer(str(val))]
                        )
                component_run.add_inputs(input_pointers)
                component_run.add_outputs(output_pointers)

            # Define tracer
            def tracer(frame, event, arg):
                if event == "call":
                    if (
                        frame.f_code.co_name == function_name
                        and frame.f_code.co_filename == filename
                    ):
                        return trace_helper
                    return

            # Run function under the tracer
            sys.settrace(tracer)
            try:
                value = func(*args, **kwargs)
            finally:
                sys.settrace(None)

            # Log relevant info
            component_run.set_end_timestamp()
            input_pointers = [store.get_io_pointer(inp) for inp in inputs]
            output_pointers = (
                [store.get_io_pointer(out, PointerTypeEnum.ENDPOINT) for out in outputs]
                if endpoint
                else [store.get_io_pointer(out) for out in outputs]
            )
            component_run.add_inputs(input_pointers)
            component_run.add_outputs(output_pointers)
            store.set_dependencies_from_inputs(component_run)

            # Add code versions
            try:
                repo = git.Repo(search_parent_directories=True)
                component_run.set_git_hash(str(repo.head.object.hexsha))
            except:
                logging.info("No git repo found.")

            # Add source code if less than 2^16
            func_source_code = inspect.getsource(func)
            if len(func_source_code) < 2 ** 16:
                component_run.set_code_snapshot(bytes(func_source_code, "ascii"))

            # Commit component run object to the DB
            store.commit_component_run(component_run)

            return value

        return wrapper

    return actual_decorator


def get_git_hash() -> str:
    """Gets hash of the parent git repo."""
    try:
        repo = git.Repo(search_parent_directories=True)
        return str(repo.head.object.hexsha)
    except:
        logging.info("No git repo found.")

    return None


# ------------------------- Basic retrieval functions ------------------------ #


def get_history(
    component_name: str,
    limit: int = 10,
    date_lower: typing.Union[datetime, str] = datetime.min,
    date_upper: typing.Union[datetime, str] = datetime.max,
) -> typing.List[ComponentRun]:
    """Returns a list of ComponentRuns that are part of the component's
    history."""
    store = Store(_db_uri)

    # Check if none
    if not date_lower:
        date_lower = datetime.min
    if not date_upper:
        date_upper = datetime.max

    history = store.get_history(component_name, limit, date_lower, date_upper)

    # Convert to client-facing ComponentRuns
    component_runs = []
    for cr in history:
        inputs = [
            IOPointer.from_dictionary(iop.__dict__).to_dictionary() for iop in cr.inputs
        ]
        outputs = [
            IOPointer.from_dictionary(iop.__dict__).to_dictionary()
            for iop in cr.outputs
        ]
        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update({"inputs": inputs, "outputs": outputs, "dependencies": dependencies})
        component_runs.append(ComponentRun.from_dictionary(d))

    return component_runs


def get_components_with_owner(owner: str) -> typing.List[Component]:
    """Returns a list of all the components associated with the specified
    order."""
    store = Store(_db_uri)
    res = store.get_components_with_owner(owner)

    # Convert to client-facing Components
    components = []
    for c in res:
        tags = [tag.name for tag in c.tags]
        d = copy.deepcopy(c.__dict__)
        d.update({"tags": tags})
        components.append(Component.from_dictionary(d))

    return components


def get_component_information(component_name: str) -> Component:
    """Returns a Component with the name, info, owner, and tags."""
    store = Store(_db_uri)
    c = store.get_component(component_name)
    if not c:
        raise RuntimeError(f"Component with name {component_name} not found.")
    tags = [tag.name for tag in c.tags]
    d = copy.deepcopy(c.__dict__)
    d.update({"tags": tags})
    return Component.from_dictionary(d)


def get_component_run_information(component_run_id: str) -> ComponentRun:
    """Returns a ComponentRun object."""
    store = Store(_db_uri)
    cr = store.get_component_run(component_run_id)
    if not cr:
        raise RuntimeError(f"Component run with id {id} not found.")
    inputs = [
        IOPointer.from_dictionary(iop.__dict__).to_dictionary() for iop in cr.inputs
    ]
    outputs = [
        IOPointer.from_dictionary(iop.__dict__).to_dictionary() for iop in cr.outputs
    ]
    dependencies = [dep.component_name for dep in cr.dependencies]
    d = copy.deepcopy(cr.__dict__)
    if cr.code_snapshot:
        d.update({"code_snapshot": str(cr.code_snapshot.decode("utf-8"))})
    d.update({"inputs": inputs, "outputs": outputs, "dependencies": dependencies})
    return ComponentRun.from_dictionary(d)


def get_components_with_tag(tag: str) -> typing.List[Component]:
    """Returns a list of components with the specified tag."""
    store = Store(_db_uri)
    res = store.get_components_with_tag(tag)

    # Convert to client-facing Components
    components = []
    for c in res:
        tags = [tag.name for tag in c.tags]
        d = copy.deepcopy(c.__dict__)
        d.update({"tags": tags})
        components.append(Component.from_dictionary(d))

    return components


def get_recent_run_ids(limit: int = 50):
    """Returns most recent component run ids."""
    store = Store(_db_uri)
    return store.get_recent_run_ids(limit)


def get_io_pointer(io_pointer_id: str, create=True):
    """Returns IO Pointer metadata."""
    store = Store(_db_uri)
    iop = store.get_io_pointer(io_pointer_id, create)
    return IOPointer.from_dictionary(iop.__dict__)


# ------------------------ Complex retrieval functions ----------------------- #


def backtrace(output_pointer: str):
    """Prints trace for an output id.
    Returns list of tuples (level, ComponentRun) where level is how
    many hops away the node is from the node that produced the output_id."""
    store = Store(_db_uri)
    trace = store.trace(output_pointer)

    # Convert to entities.ComponentRun
    component_runs = []
    for depth, cr in trace:
        inputs = [IOPointer.from_dictionary(iop.__dict__) for iop in cr.inputs]
        outputs = [IOPointer.from_dictionary(iop.__dict__) for iop in cr.outputs]
        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update({"inputs": inputs, "outputs": outputs, "dependencies": dependencies})
        component_runs.append((depth, ComponentRun.from_dictionary(d)))

    return component_runs


def web_trace(output_id: str):
    store = Store(_db_uri)
    return store.web_trace(output_id)
