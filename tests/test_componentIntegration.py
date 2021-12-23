import unittest
import pandas as pd
from mltrace import Test, Component, set_db_uri


class TestTest(unittest.TestCase):
    def setUp(self):
        set_db_uri("test")

    def testBeforeTestHasAllVars(self):
        class DummyTest(Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: str):
                testVal = n + "_before"
                if testVal != "test_before":
                    raise Exception("Wrong Value")

        c = Component(
            "aditi", "test", "test_description", beforeTests=[DummyTest]
        )

        @c.run
        def function(n: str = "test"):
            return

    def testBeforeTestNotHaveAllVars(self):
        class DummyTest(Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: int):
                testVal = n * 10
                if testVal != 10:
                    raise Exception("Wrong Value")

        c = Component(
            "aditi", "test", "test_description", beforeTests=[DummyTest]
        )

        @c.run
        def function():
            n = 1
            return

        with self.assertRaises(Exception):
            function()

    def testAfterTestHasAllVars(self):
        class DummyTest(Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: str):
                testVal = n + "check"
                print(n)
                if testVal != "test_aftercheck":
                    raise Exception("Wrong Value")

        c = Component(
            "aditi", "test", "test_description", afterTests=[DummyTest]
        )

        @c.run
        def function(n: str = "test"):
            n += "_after"
            return

    def testAfterTestNotHaveAllVars(self):
        class DummyTest(Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: int):
                testVal = n * 10
                if testVal != 10:
                    raise Exception("Wrong Value")

        c = Component(
            "aditi", "test", "test_description", afterTests=[DummyTest]
        )

        @c.run
        def function():
            k = 1
            return

        with self.assertRaises(Exception):
            function()

    def testValueChange(self):
        class BeforeTest(Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, data: pd.DataFrame):
                testVal = data["A"].mean()
                if testVal != 2:
                    raise Exception("Wrong Value in Before Test")

        class AfterTest(Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, data: pd.DataFrame):
                testVal = data["A"].mean()
                if testVal != 4:
                    raise Exception("Wrong Value in After Test")

        c = Component(
            "aditi",
            "test",
            "test_description",
            beforeTests=[BeforeTest],
            afterTests=[AfterTest],
        )

        @c.run
        def function(data: pd.DataFrame):
            data = data.replace([0, 1, 2, 3], 4)
            return

        df = pd.DataFrame({"A": [0, 1, 2, 3, 4], "B": [5, 6, 7, 8, 9]})

        function(df)
