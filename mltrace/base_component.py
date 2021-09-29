"""
Base Component class. Other components should inherit from this class.
"""
from abc import ABC, abstractmethod

import functools
import inspect

class Component(ABC):
    def __init__(self, name: str = "", username: str = "", beforeTests = list, afterTests = list):
        """Default constructor. User can override."""
        self.name = name
        self.username = username
        self.beforeTests = beforeTests
        self.afterTests = afterTests

    @abstractmethod
    def beforeRun(self):
        """Computation to execute before running a component."""
        pass

    @abstractmethod
    def afterRun(self):
        """Computation to execute after running a component."""
        pass

    def run(self, *user_args, **user_kwargs):
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
        """
        inv_user_kwargs = {v: k for k, v in user_kwargs.items()}
        key_names = ["skip_before_run", "skip_after_run"]

        def actual_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
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
                    before_run_args = {
                        k: v
                        for k, v in all_args.items()
                        if k in inspect.signature(self.beforeRun).parameters
                    }
                    self.beforeRun(**before_run_args)

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
                    after_run_args = {
                        k: v
                        for k, v in after_run_args.items()
                        if k in inspect.signature(self.afterRun).parameters
                    }
                    self.afterRun(**after_run_args)

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