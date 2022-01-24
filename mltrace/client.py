from datetime import datetime
from mltrace import utils
from mltrace.db import Store, PointerTypeEnum
from mltrace.db.utils import _get_data_and_model_args, _load, _save
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

_db_uri = utils.get_db_uri()

# --------------------- Database management functions ------------------- #


def set_db_uri(uri: str):
    global _db_uri
    utils.set_db_uri(uri)
    _db_uri = uri


def get_db_uri() -> str:
    global _db_uri
    return utils.get_db_uri()


def set_address(address: str):
    global _db_uri
    _db_uri = utils.set_address(address)


def clean_db():
    """Deletes database and reinitializes tables."""
    store = Store(_db_uri, delete_first=True)


# ----------------------- Load and save functions ---------------------- #


def load(pathname: str):
    """Loads joblib file at pathname."""
    return _load(pathname)


# TODO(shreyashankar): Handle multiple writes at the same second
def save(obj, pathname: str = None) -> str:
    """Saves joblib object to pathname."""
    return _save(obj, pathname)


# ----------------------- Creation functions ---------------------------- #


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


def log_component_run(
    component_run: ComponentRun,
    set_dependencies_from_inputs=True,
    staleness_threshold: int = (60 * 60 * 24 * 30),
):
    """Takes client-facing ComponentRun object and logs it to the DB."""
    store = Store(_db_uri)

    # Make dictionary object
    component_run_dict = component_run.to_dictionary()

    component_run_sql = store.initialize_empty_component_run(
        component_run.component_name
    )

    # Add relevant attributes
    if component_run_dict["start_timestamp"]:
        component_run_sql.set_start_timestamp(
            component_run_dict["start_timestamp"]
        )

    if component_run_dict["end_timestamp"]:
        component_run_sql.set_end_timestamp(
            component_run_dict["end_timestamp"]
        )

    if component_run_dict["notes"]:
        component_run_sql.add_notes(component_run_dict["notes"])

    component_run_sql.set_git_hash(component_run_dict["git_hash"])
    component_run_sql.set_git_tags(component_run_dict["git_tags"])
    component_run_sql.set_code_snapshot(component_run_dict["code_snapshot"])

    # Add I/O
    component_run_sql.add_inputs(
        [
            store.get_io_pointer(
                inp.name, inp.value, pointer_type=inp.pointer_type
            )
            for inp in component_run_dict["inputs"]
        ]
    )
    component_run_sql.add_outputs(
        [
            store.get_io_pointer(
                out.name, out.value, pointer_type=out.pointer_type
            )
            for out in component_run_dict["outputs"]
        ]
    )

    # Create component if it does not exist
    create_component(component_run.component_name, "", "")

    # Add dependencies if there is flag to automatically set
    if set_dependencies_from_inputs:
        store.set_dependencies_from_inputs(component_run_sql)

    # Add dependencies explicitly stored in the component run
    for dependency in component_run_dict["dependencies"]:
        cr = store.get_history(dependency, 1)[0]
        component_run_sql.set_upstream(cr)

    store.commit_component_run(
        component_run_sql, staleness_threshold=staleness_threshold
    )


def create_random_ids(num_outputs=1) -> typing.List[str]:
    """Returns a list of num_outputs ids
    that a client can use to tag outputs."""

    return [str(uuid.uuid4()) for _ in range(num_outputs)]


# Log input strings
# function to apply to outputs to log those

# TODO(shreyashankar): change logging.debug to thrown errors
def register(
    component_name: str,
    inputs: typing.List[str] = [],
    outputs: typing.List[str] = [],
    input_vars: typing.List[str] = [],
    output_vars: typing.List[str] = [],
    input_kwargs: typing.Dict[str, str] = {},
    output_kwargs: typing.Dict[str, str] = {},
    endpoint: bool = False,
    staleness_threshold: int = (60 * 60 * 24 * 30),
    auto_log: bool = False,
):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function information
            filename = inspect.getfile(func)
            function_name = func.__name__

            # Construct component run object
            store = Store(_db_uri)
            component_run = store.initialize_empty_component_run(
                component_name
            )
            component_run.set_start_timestamp()

            # Define trace helper
            frame = None
            trace = sys.gettrace()

            def trace_helper(_frame, event, arg):
                nonlocal frame
                if frame is None and event == "call":
                    frame = _frame
                    sys.settrace(trace)
                    return trace

            # Run function under the tracer
            sys.settrace(trace_helper)
            try:
                # merge with existing run
                value = func(*args, **kwargs)
            finally:
                sys.settrace(trace)

            component_run.set_end_timestamp()

            # Do logging here
            logging.info(f"Inspecting {frame.f_code.co_filename}")
            input_pointers = []
            output_pointers = []
            local_vars = frame.f_locals

            # Auto log inputs
            if auto_log:
                # Get IOPointers corresponding to args and f_locals
                all_input_args = {
                    k: v.default
                    for k, v in inspect.signature(func).parameters.items()
                    if v.default is not inspect.Parameter.empty
                }
                all_input_args = {
                    **all_input_args,
                    **dict(zip(inspect.getfullargspec(func).args, args)),
                }
                all_input_args = {**all_input_args, **kwargs}
                input_pointers += store.get_io_pointers_from_args(
                    **all_input_args
                )

            # Add input_vars and output_vars as pointers
            for var in input_vars:
                if var not in local_vars:
                    raise ValueError(
                        f"Variable {var} not in current stack frame."
                    )
                val = local_vars[var]
                if val is None:
                    logging.debug(f"Variable {var} has value {val}.")
                    continue
                if isinstance(val, list):
                    input_pointers += store.get_io_pointers(val)
                else:
                    input_pointers.append(store.get_io_pointer(str(val)))
            for var in output_vars:
                if var not in local_vars:
                    raise ValueError(
                        f"Variable {var} not in current stack frame."
                    )
                val = local_vars[var]
                if val is None:
                    logging.debug(f"Variable {var} has value {val}.")
                    continue
                if isinstance(val, list):
                    output_pointers += (
                        store.get_io_pointers(
                            val, pointer_type=PointerTypeEnum.ENDPOINT
                        )
                        if endpoint
                        else store.get_io_pointers(val)
                    )
                else:
                    output_pointers += (
                        [
                            store.get_io_pointer(
                                str(val), pointer_type=PointerTypeEnum.ENDPOINT
                            )
                        ]
                        if endpoint
                        else [store.get_io_pointer(str(val))]
                    )
            # Add input_kwargs and output_kwargs as pointers
            for key, val in input_kwargs.items():
                if key not in local_vars or val not in local_vars:
                    raise ValueError(
                        f"Variables ({key}, {val}) not in current stack frame."
                    )
                if local_vars[key] is None:
                    logging.debug(
                        f"Variable {key} has value {local_vars[key]}."
                    )
                    continue
                if isinstance(local_vars[key], list):
                    if not isinstance(local_vars[val], list) or len(
                        local_vars[key]
                    ) != len(local_vars[val]):
                        raise ValueError(
                            f'Value "{val}" does not have the same length as'
                            + f' the key "{key}."'
                        )
                    input_pointers += store.get_io_pointers(
                        local_vars[key], values=local_vars[val]
                    )
                else:
                    input_pointers.append(
                        store.get_io_pointer(
                            str(local_vars[key]), local_vars[val]
                        )
                    )
            for key, val in output_kwargs.items():
                if key not in local_vars or val not in local_vars:
                    raise ValueError(
                        f"Variables ({key}, {val}) not in current stack frame."
                    )
                if local_vars[key] is None:
                    logging.debug(
                        f"Variable {key} has value {local_vars[key]}."
                    )
                    continue
                if isinstance(local_vars[key], list):
                    if not isinstance(local_vars[val], list) or len(
                        local_vars[key]
                    ) != len(local_vars[val]):
                        raise ValueError(
                            f'Value "{val}" does not have the same length as'
                            + f' the key "{key}."'
                        )
                    output_pointers += (
                        store.get_io_pointers(
                            local_vars[key],
                            local_vars[val],
                            pointer_type=PointerTypeEnum.ENDPOINT,
                        )
                        if endpoint
                        else store.get_io_pointers(
                            local_vars[key], local_vars[val]
                        )
                    )
                else:
                    output_pointers += (
                        [
                            store.get_io_pointer(
                                str(local_vars[key]),
                                local_vars[val],
                                pointer_type=PointerTypeEnum.ENDPOINT,
                            )
                        ]
                        if endpoint
                        else [
                            store.get_io_pointer(
                                str(local_vars[key]), local_vars[val]
                            )
                        ]
                    )

            # Directly specified I/O
            if not callable(inputs):
                input_pointers += [store.get_io_pointer(inp) for inp in inputs]
            input_pointers += [store.get_io_pointer(inp) for inp in inputs]
            output_pointers += (
                [
                    store.get_io_pointer(
                        out, pointer_type=PointerTypeEnum.ENDPOINT
                    )
                    for out in outputs
                ]
                if endpoint
                else [store.get_io_pointer(out) for out in outputs]
            )

            # If there were calls to mltrace.load and mltrace.save, log them
            if "_mltrace_loaded_artifacts" in local_vars:
                input_pointers += [
                    store.get_io_pointer(name, val)
                    for name, val in local_vars[
                        "_mltrace_loaded_artifacts"
                    ].items()
                ]
            if "_mltrace_saved_artifacts" in local_vars:
                output_pointers += [
                    store.get_io_pointer(name, val)
                    for name, val in local_vars[
                        "_mltrace_saved_artifacts"
                    ].items()
                ]

            func_source_code = inspect.getsource(func)
            if auto_log:
                # Get IOPointers corresponding to args and f_locals
                all_output_args = {
                    k: v
                    for k, v in local_vars.items()
                    if k not in all_input_args
                }
                output_pointers += store.get_io_pointers_from_args(
                    **all_output_args
                )

            component_run.add_inputs(input_pointers)
            component_run.add_outputs(output_pointers)

            # Add code versions
            try:
                repo = git.Repo(search_parent_directories=True)
                component_run.set_git_hash(str(repo.head.object.hexsha))
            except Exception as e:
                logging.info("No git repo found.")

            # Add git tags
            if get_git_tags() is not None:
                component_run.set_git_tags(get_git_tags())

            # Add source code if less than 2^16
            if len(func_source_code) < 2 ** 16:
                component_run.set_code_snapshot(
                    bytes(func_source_code, "ascii")
                )

            # Create component if it does not exist
            create_component(component_run.component_name, "", "")

            store.set_dependencies_from_inputs(component_run)

            # Commit component run object to the DB
            store.commit_component_run(
                component_run, staleness_threshold=staleness_threshold
            )

            return value

        return wrapper

    return actual_decorator


def get_git_hash() -> str:
    """Gets hash of the parent git repo."""
    try:
        repo = git.Repo(search_parent_directories=True)
        return str(repo.head.object.hexsha)
    except Exception as e:
        logging.info("No git repo found.")

    return None


def get_git_tags() -> typing.List[str]:
    """
    Gets tags associated with commit of parent git repo, if exists
    ref:https://stackoverflow.com/questions/34932306/get-tags-of-a-commit
    """
    try:
        tagmap = {}
        repo = git.Repo(search_parent_directories=True)
        for t in repo.tags:
            tagmap.setdefault(repo.commit(t), []).append(t)
        tags = tagmap[repo.commit(repo.head.object.hexsha)]
        return [tag.name for tag in tags]
    except Exception as e:
        logging.info("No git tag found")


def add_notes_to_component_run(component_run_id: str, notes: str) -> str:
    """Adds notes to component run."""
    store = Store(_db_uri)
    return store.add_notes_to_component_run(component_run_id, notes)


def flag_output_id(output_id: str) -> bool:
    """Sets the flag property of an IOPointer to true."""
    store = Store(_db_uri)
    return store.set_io_pointer_flag(output_id, True)


def unflag_output_id(output_id: str) -> bool:
    """Sets the flag property of an IOPointer to false."""
    store = Store(_db_uri)
    return store.set_io_pointer_flag(output_id, False)


def unflag_all():
    store = Store(_db_uri)
    store.unflag_all()


# ----------------- Basic retrieval functions ------------------- #


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
            IOPointer.from_dictionary(iop.__dict__).to_dictionary()
            for iop in cr.inputs
        ]
        outputs = [
            IOPointer.from_dictionary(iop.__dict__).to_dictionary()
            for iop in cr.outputs
        ]
        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update(
            {
                "inputs": inputs,
                "outputs": outputs,
                "dependencies": dependencies,
            }
        )
        component_runs.append(ComponentRun.from_dictionary(d))

    return component_runs


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
        IOPointer.from_dictionary(iop.__dict__).to_dictionary()
        for iop in cr.inputs
    ]
    outputs = [
        IOPointer.from_dictionary(iop.__dict__).to_dictionary()
        for iop in cr.outputs
    ]
    dependencies = [dep.component_name for dep in cr.dependencies]
    d = copy.deepcopy(cr.__dict__)
    if cr.code_snapshot:
        d.update({"code_snapshot": str(cr.code_snapshot.decode("utf-8"))})
    d.update(
        {"inputs": inputs, "outputs": outputs, "dependencies": dependencies}
    )

    return ComponentRun.from_dictionary(d)


def get_components(tag="", owner="") -> typing.List[Component]:
    """Returns all components with the specified owner and/or tag.
    Else, returns all components."""
    store = Store(_db_uri)
    res = store.get_components(tag=tag, owner=owner)

    # Convert to client-facing Components
    components = []
    for c in res:
        tags = [tag.name for tag in c.tags]
        d = copy.deepcopy(c.__dict__)
        d.update({"tags": tags})
        components.append(Component.from_dictionary(d))

    return components


def get_recent_run_ids(limit: int = 5, last_run_id=None):
    """Returns most recent component run ids."""
    store = Store(_db_uri)
    return store.get_recent_run_ids(limit, last_run_id)


def get_io_pointer(
    io_pointer_id: str, io_pointer_val: typing.Any = None, create=True
):
    """Returns IO Pointer metadata."""
    store = Store(_db_uri)
    iop = store.get_io_pointer(io_pointer_id, io_pointer_val, create=create)
    return IOPointer.from_dictionary(iop.__dict__)


def get_tags() -> typing.List[str]:
    store = Store(_db_uri)
    res = store.get_tags()
    tags = [t.name for t in res]
    return tags

# --------------- Complex retrieval functions ------------------ #


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
        outputs = [
            IOPointer.from_dictionary(iop.__dict__) for iop in cr.outputs
        ]
        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update(
            {
                "inputs": inputs,
                "outputs": outputs,
                "dependencies": dependencies,
            }
        )
        component_runs.append((depth, ComponentRun.from_dictionary(d)))

    return component_runs


def web_trace(output_id: str):
    store = Store(_db_uri)
    return store.web_trace(output_id, last_only=True)


def review_flagged_outputs():
    """Finds common ComponentRuns for a group of flagged outputs.
    Returns a list of ComponentRuns and occurrence counts in the
    group of flagged outputs, sorted by descending count and then
    alphabetically."""
    store = Store(_db_uri)
    return store.review_flagged_outputs()


def retract_label(label_id: str):
    store = Store(_db_uri)
    store.delete_label(label_id)


def retract_labels(label_ids: typing.List[str]):
    store = Store(_db_uri)
    store.delete_labels(label_ids)


def retrieve_retracted_labels():
    store = Store(_db_uri)
    return store.retrieve_deleted_labels()


def retrieve_io_pointers_for_label(label_id: str):
    store = Store(_db_uri)
    iops = store.retrieve_io_pointers_for_label(label_id)
    return [IOPointer.from_dictionary(iop.__dict__) for iop in iops]


def get_labels() -> typing.List[str]:
    store = Store(_db_uri)
    return [label.id for label in store.get_all_labels()]


def create_labels(label_ids: typing.List[str]):
    store = Store(_db_uri)
    store.get_labels(label_ids)


def log_output(
    task_name: str,
    identifier: str,
    val: float,
):
    store = Store(_db_uri)
    store.log_output(identifier=identifier, task_name=task_name, val=val)


def log_feedback(
    task_name: str,
    identifier: str,
    val: float,
):
    store = Store(_db_uri)
    store.log_feedback(identifier=identifier, task_name=task_name, val=val)


def compute_metric(
    task_name: str,
    metric_fn: typing.Callable,
    window_size: int = None,
):
    store = Store(_db_uri)
    store.compute_metric(task_name, metric_fn, window_size)
