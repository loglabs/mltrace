"""
Base class for test objects.
"""

import inspect, typing


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
            result = getattr(self, method.__name__)(**test_args) # is this calling the test? returning result?
            status[method.__name__] = result
