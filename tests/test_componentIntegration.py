import unittest
import pandas as pd
from mltrace.entities import base_test, base_component


class TestTest(unittest.TestCase):
    def testBeforeTestHasAllVars(self):
        class DummyTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: int):
                testVal = n * 10
                if testVal != 10:
                    raise Exception("Wrong Value")

        c = base_component.Component("aditi", "test", "test_description", beforeTests=[DummyTest])

        @c.run(
            component_name="test_component",
            input_vars=["n"],
            output_vars=[],
        )
        def function(n: int = 1):
            return


    def testBeforeTestNotHaveAllVars(self):
        class DummyTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: int):
                testVal = n * 10
                if testVal != 10:
                    raise Exception("Wrong Value")

        c = base_component.Component("aditi", "test", "test_description", beforeTests=[DummyTest])

        @c.run(
            component_name="test_component",
            input_vars=[],
            output_vars=["n"],
        )
        def function():
            n = 1
            return

        with self.assertRaises(Exception):
            function()

    def testAfterTestHasAllVars(self):
        class DummyTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: int):
                testVal = n * 10
                print(n)
                if testVal != 10:
                    raise Exception("Wrong Value")

        c = base_component.Component("aditi", "test", "test_description", afterTests=[DummyTest])

        @c.run(
            component_name="test_component",
            input_vars=["n"],
            output_vars=["n"],
        )
        def function(n: int = 1):
            n += 2
            return

    def testAfterTestNotHaveAllVars(self):
        class DummyTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: int):
                testVal = n * 10
                if testVal != 10:
                    raise Exception("Wrong Value")

        c = base_component.Component("aditi", "test", "test_description", afterTests=[DummyTest])

        @c.run(
            component_name="test_component",
            input_vars=[],
            output_vars=["n"],
        )
        def function():
            k = 1
            return

        with self.assertRaises(Exception):
            function()

    def testValueChange(self):
        class BeforeTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, data: pd.DataFrame):
                testVal = data["A"].mean()
                if testVal != 2:
                    raise Exception("Wrong Value in Before Test")

        class AfterTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, data: pd.DataFrame):
                testVal = data["A"].mean()
                if testVal != 4:
                    raise Exception("Wrong Value in After Test")

        c = base_component.Component(
            "aditi",
            "test",
            "test_description",
            beforeTests=[BeforeTest],
            afterTests=[AfterTest]
        )

        @c.run(
            component_name="test_component",
            input_vars=["data"],
            output_vars=["data"],
        )
        def function(data: pd.DataFrame):
            data.replace([0, 1, 2, 3], 4)
            return

        df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
                           'B': [5, 6, 7, 8, 9]}
                          )

        function()


