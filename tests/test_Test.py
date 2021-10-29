import unittest
from mltrace.entities import base_test, base_component


class TestTest(unittest.TestCase):

    def testRunsAllTestFunc(self):
        class DummyTest(base_test.Test):
            def __init__(self):
                super().__init__("Dummy")

            def testCorrect(self, n: list):
                n[0] += 10
                print("testCorrect called")

            def testAlsoCorrect(self, n: list):
                n[0] += 10
                print("testAlsoCorrect called")

            def TestNotCorrect(self, n: list):
                raise Exception("TestNotCorrect called!")

        c = base_component.Component("aditi", "test", "test_description", afterTests=[DummyTest])
        val = [100]

        @c.run(
            component_name="test_component",
            input_vars=[],
            output_vars=["n"],
        )
        def function():
            n = val
            return

        function()
        self.assertTrue(val[0]==120)

    def testRunsOnlyTestFunc(self):
        return
