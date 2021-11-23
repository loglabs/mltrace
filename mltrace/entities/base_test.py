"""
Base class for test objects.
"""

import inspect
from mltrace.entities.utils import MLTraceError


class Test(object):
    def __init__(self, name: str = ""):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def getTestMethods(self):
        """
        Gets all methods in this class that start with "test"
        """
        methods = inspect.getmembers(self, inspect.ismethod)
        testMethods = [
            function for name, function in methods if name.startswith("test")
        ]
        return testMethods

    def runTests(self, **kwargs) -> {}:
        """
        Runs all tests in this class.
        """
        testMethods = self.getTestMethods()
        status = {}
        for method in testMethods:
            test_args = {
                k: v
                for k, v in kwargs.items()
                if k in inspect.signature(method).parameters
            }
            try:
                getattr(self, method.__name__)(**test_args)
                status[method.__name__] = "success"
            except MLTraceError as e:
                status[method.__name__] = "fail"
                if len(str(e)) != 0:
                    status[method.__name__] += ", error: " + str(e)
                    print("Test " + method.__name__ + " failed: " + str(e))
                else:
                    print("Test " + method.__name__ + " failed")

        return status

    def assertEqual(self, a, b, msg = None):
        if not a == b:
            raise MLTraceError(msg)

    # assertNOTequl, less than, less than Eual, greater than Equal, assert true, assert false

    def assertGreater(self, a, b, msg = None):
        if not a > b:
            raise MLTraceError(msg)

