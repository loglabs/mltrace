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
            afterTests: list = []
    ):
        """Components abstraction.
        Components should have a name, owner, and lists of before and after tests to run.
        Optionally they will have tags."""
        print("afterrun, basecomp", afterTests)
        self._name = name
        self._owner = owner
        self._description = description
        self._beforeTests = beforeTests
        self._afterTests = afterTests

    def beforeRun(self, **kwargs):
        """Computation to execute before running a component. Will run each test object listed in beforeTests."""
        for test in self._beforeTests:
            # get all methods of the test:
            testFunctions = inspect.getmembers(test)

            # make test oject
            testObj = test()

            # for each function in the test
            for name, function in testFunctions:
                if name[0:4] == 'test':
                    test_args = {
                        k: v
                        for k, v in kwargs.items()
                        if k in inspect.signature(function).parameters
                    }

                    getattr(testObj, function.__name__)(**test_args)

        # pass all args to beforeRun,in beforRun parse through the pargs to pass in the values need to the correct tests

    def afterRun(self, **local_vars):
        """Computation to execute after running a component. Will run all test objects listed in afterTests."""
        for test in self._afterTests:
            # get all methods of the test:
            testFunctions = inspect.getmembers(test)

            testObj = test()

            # for each function in the test
            for name, function in testFunctions:
                if name[0:4] == 'test':
                    test_args = {
                        k: v
                        for k, v in local_vars.items()
                        if k in inspect.signature(function).parameters
                    }

                    getattr(testObj, function.__name__)(**test_args)

    def run(self,
            inputs: typing.List[str] = [],
            outputs: typing.List[str] = [],
            input_vars: typing.List[str] = [],
            output_vars: typing.List[str] = [],
            input_kwargs: typing.Dict[str, str] = {},
            output_kwargs: typing.Dict[str, str] = {},
            endpoint: bool = False,
            staleness_threshold: int = (60 * 60 * 24 * 30),
            *user_args,
            **user_kwargs
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
            then the afterRun method with the values of the args at the end of the
            function.

        ADD DESCRITION HERE ABOUT INPUT VARIABLEs and what they are
        """
        inv_user_kwargs = {v: k for k, v in user_kwargs.items()}
        key_names = ["skip_before_run", "skip_after_run"]

        def actual_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Get function information
                filename = inspect.getfile(func)
                function_name = func.__name__

                # Construct component run object
                store = Store(clientUtils.get_db_uri())
                component_run = store.initialize_empty_component_run(
                    self.name
                )
                component_run.set_start_timestamp()

                # Assert key names are not in args or kwargs
                if (
                        set(key_names) & set(inspect.getfullargspec(func).args)
                ) or (set(key_names) & set(kwargs.keys())):
                    raise ValueError(
                        f"skip_before_run or skip_after_run cannot be in the arguments of the function {func.__name__}"
                    )

                # Run before test
                if not user_kwargs.get("skip_before_run"):
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

                # Run function
                f_locals, value = utils.run_func_capture_locals(
                    func, *args, **kwargs
                )

                if not user_kwargs.get("skip_after_run"):
                    # Run after test
                    after_run_args = {
                        k
                        if k not in inv_user_kwargs
                        else inv_user_kwargs[k]: v
                        for k, v in f_locals.items()
                    }
                self.afterRun(**f_locals)

                # add logging stuff from register here
                logging.info(f"Inspecting {filename}, function {function_name}")
                input_pointers = []
                output_pointers = []
                local_vars = f_locals

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

                    component_run.add_inputs(input_pointers)
                    component_run.add_outputs(output_pointers)

                    # Log relevant info
                    component_run.set_end_timestamp()
                    input_pointers = [store.get_io_pointer(inp) for inp in inputs]
                    output_pointers = (
                        [
                            store.get_io_pointer(
                                out, pointer_type=PointerTypeEnum.ENDPOINT
                            )
                            for out in outputs
                        ]
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
                    except Exception as e:
                        logging.info("No git repo found.")

                    # Add git tags
                    if client.get_git_tags() is not None:
                        component_run.set_git_tags(client.get_git_tags())

                    # Add source code if less than 2^16
                    func_source_code = inspect.getsource(func)
                    if len(func_source_code) < 2 ** 16:
                        component_run.set_code_snapshot(
                            bytes(func_source_code, "ascii")
                        )

                    # Commit component run object to the DB
                    store.commit_component_run(
                        component_run, staleness_threshold=staleness_threshold
                    )

                    return value

            return wrapper

        if (
                len(user_args) == 1
                and len(user_kwargs) == 0
                and callable(user_args[0])
        ):
            # Used decorator without arguments
            func = user_args[0]

            return actual_decorator(func)

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
    def beforeTests(self) -> list:
        return self._beforeTests

    @property
    def afterTests(self) -> list:
        return self._afterTests

    def __repr__(self):
        params = self.to_dictionary()
        return json.dumps(params)
