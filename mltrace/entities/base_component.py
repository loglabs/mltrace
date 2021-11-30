"""
Base Component class. Other components should inherit from this class.
"""
import json
import logging
import typing

from mltrace import client
from mltrace import utils as clientUtils
from mltrace.db import Store, PointerTypeEnum
from mltrace.entities import utils
from mltrace.entities.base import Base

import functools
import inspect
import git


class Component(Base):
    def __init__(
        self,
        name: str = "",
        owner: str = "",
        description: str = "",
        beforeTests: list = [],
        afterTests: list = [],
        tags: typing.List[str] = [],
    ):
        """Components abstraction.
        Components should have a name, owner, and lists
        of before and after tests to run. Optionally they will have tags."""
        self._name = name
        self._owner = owner
        self._description = description
        self._tags = tags
        self._beforeTests = beforeTests
        self._afterTests = afterTests

    def beforeRun(self, **kwargs):
        """Computation to execute before running a component.
        Will run each test object listed in beforeTests."""
        for test in self._beforeTests:
            test().runTests(**kwargs)

    def afterRun(self, **local_vars):
        """Computation to execute after running a component.
        Will run all test objects listed in afterTests."""
        for test in self._afterTests:
            test().runTests(**local_vars)

    def run(
        self,
        input_filenames: typing.List[str] = [],
        output_filenames: typing.List[str] = [],
        input_vars: typing.List[str] = [],
        output_vars: typing.List[str] = [],
        input_kwargs: typing.Dict[str, str] = {},
        output_kwargs: typing.Dict[str, str] = {},
        endpoint: bool = False,
        staleness_threshold: int = (60 * 60 * 24 * 30),
        auto_log: bool = False,
        *user_args,
        **user_kwargs,
    ):
        """
        Decorator around the function executed:
        c = Component()
        @c.run
        def my_function(arg1, arg2):
                do_something()
            arg1 and arg2 are the arguments passed to the
            beforeRun and afterRun methods.
            We first execute the beforeRun method, then the function itself,
            then the afterRun method with the values of the args at the
            end of the function.

        @:param input_filenames - string variable representing the variable
            of the input
        @:param output_filenames - string variable representing the variable
            of the output
        @:param input_vars - list of variables representing inputs
        @:param output_vars - list of variables representing outputs
        @:param input_kwargs - string variable representing the file name
            of the input
        @:param output_kwargs - string variable representing the file name
            of the output
        """
        inv_user_kwargs = {v: k for k, v in user_kwargs.items()}
        key_names = ["skip_before", "skip_after"]

        def actual_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Construct component run object
                store = Store(clientUtils.get_db_uri())
                component_run = store.initialize_empty_component_run(self.name)
                component_run.set_start_timestamp()

                # Assert key names are not in args or kwargs
                if (
                    set(key_names) & set(inspect.getfullargspec(func).args)
                ) or (set(key_names) & set(kwargs.keys())):
                    raise ValueError(
                        "skip_before or skip_after cannot be in "
                        + f"the arguments of the function {func.__name__}"
                    )

                # Run before test
                if not user_kwargs.get("skip_before"):
                    all_args = dict(
                        zip(inspect.getfullargspec(func).args, args)
                    )
                    all_args = {
                        k
                        if k not in inv_user_kwargs
                        else inv_user_kwargs[k]: v
                        for k, v in all_args.items()
                    }
                    all_args = {**all_args, **kwargs}
                    self.beforeRun(**all_args)

                # Create input and output pointers
                input_pointers = []
                output_pointers = []

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
                        should_filter=True, **all_input_args
                    )

                # Run function
                local_vars, value = utils.run_func_capture_locals(
                    func, *args, **kwargs
                )
                component_run.set_end_timestamp()

                if not callable(input_filenames):

                    duplicate = input_filenames
                    if not isinstance(duplicate, dict):
                        duplicate = {fname: None for fname in duplicate}

                    for var, label_vars in duplicate.items():
                        if var not in local_vars:
                            raise ValueError(
                                f"Variable {var} not in current stack frame."
                            )
                        val = local_vars[var]
                        labels = None
                        if label_vars is not None:
                            try:
                                labels = (
                                    [local_vars[lv] for lv in label_vars]
                                    if isinstance(label_vars, list)
                                    else local_vars[label_vars]
                                )
                                if isinstance(labels, str):
                                    labels = [labels]
                            except KeyError:
                                raise ValueError(
                                    f"Variable {label_vars} not "
                                    + f"in current stack frame."
                                )
                        if val is None:
                            logging.debug(f"Variable {var} has value {val}.")
                            continue
                        if isinstance(val, list):
                            input_pointers += store.get_io_pointers(
                                val, labels=labels
                            )
                        else:
                            input_pointers.append(
                                store.get_io_pointer(str(val), labels=labels)
                            )
                    for var in output_filenames:
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
                                        str(val),
                                        pointer_type=PointerTypeEnum.ENDPOINT,
                                    )
                                ]
                                if endpoint
                                else [store.get_io_pointer(str(val))]
                            )
                    # Add input_kwargs and output_kwargs as pointers
                    for key, val in input_kwargs.items():
                        if key not in local_vars or val not in local_vars:
                            raise ValueError(
                                f"({key}, {val}) not in current stack frame."
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
                                    f'Value "{val}" does not have the same '
                                    + f'length as the key "{key}."'
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
                                f"({key}, {val}) not in current stack frame."
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
                                    f'Value "{val}" does not have the same '
                                    + f'length as the key "{key}."'
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

                    # Log input and output vars
                    duplicate = input_vars
                    if not isinstance(duplicate, dict):
                        duplicate = {vname: None for vname in input_vars}

                    for var, label_vars in duplicate.items():
                        if var not in local_vars:
                            raise ValueError(
                                f"Variable {var} not in current stack frame."
                            )
                        val = local_vars[var]
                        labels = None
                        if label_vars is not None:
                            try:
                                labels = (
                                    [local_vars[lv] for lv in label_vars]
                                    if isinstance(label_vars, list)
                                    else local_vars[label_vars]
                                )
                                if isinstance(labels, str):
                                    labels = [labels]
                            except KeyError:
                                raise ValueError(
                                    f"Variable {label_vars} not "
                                    + f"in current stack frame."
                                )
                        if val is None:
                            logging.debug(f"Variable {var} has value {val}.")
                            continue
                        input_pointers += store.get_io_pointers_from_args(
                            should_filter=False, labels=labels, **{var: val}
                        )

                    for var in output_vars:
                        if var not in local_vars:
                            raise ValueError(
                                f"Variable {var} not in current stack frame."
                            )
                        val = local_vars[var]
                        if val is None:
                            logging.debug(f"Variable {var} has value {val}.")
                            continue
                        output_pointers += store.get_io_pointers_from_args(
                            should_filter=False, **{var: val}
                        )

                # If there were calls to mltrace.load and mltrace.save, log

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
                        should_filter=True, **all_output_args
                    )

                # Check that none of the labels in the inputs are deleted
                store.assert_not_deleted_labels(
                    input_pointers, staleness_threshold=staleness_threshold
                )

                # TODO(shreyashankar): propagate labels
                store.propagate_labels(input_pointers, output_pointers)

                component_run.add_inputs(input_pointers)
                component_run.add_outputs(output_pointers)

                # Add code versions
                try:
                    repo = git.Repo(search_parent_directories=True)
                    component_run.set_git_hash(str(repo.head.object.hexsha))
                except Exception as e:
                    logging.info("No git repo found.")

                # Add git tags
                if client.get_git_tags() is not None:
                    component_run.set_git_tags(client.get_git_tags())

                # Add source code if less than 2^16
                if len(func_source_code) < 2 ** 16:
                    component_run.set_code_snapshot(
                        bytes(func_source_code, "ascii")
                    )

                # Create component if it does not exist
                client.create_component(
                    self.name, self.description, self.owner, self.tags
                )

                # Set dependencies
                store.set_dependencies_from_inputs(component_run)

                # Commit component run object to the DB
                store.commit_component_run(
                    component_run, staleness_threshold=staleness_threshold
                )

                # Perform after run tests
                if not user_kwargs.get("skip_after"):
                    # Run after test
                    after_run_args = {
                        k
                        if k not in inv_user_kwargs
                        else inv_user_kwargs[k]: v
                        for k, v in local_vars.items()
                    }
                    self.afterRun(**after_run_args)

                return value

            return wrapper

        if callable(input_filenames):
            # Used decorator without arguments
            return actual_decorator(input_filenames)

        else:
            # User passed in some kwargs
            return actual_decorator

    @property
    def name(self) -> str:
        return self._name

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def description(self) -> str:
        return self._description

    @property
    def tags(self) -> typing.List[str]:
        return self._tags

    @property
    def beforeTests(self) -> list:
        return self._beforeTests

    @property
    def afterTests(self) -> list:
        return self._afterTests

    def __repr__(self):
        params = self.to_dictionary()
        del params["beforeTests"]
        del params["afterTests"]
        return json.dumps(params)
