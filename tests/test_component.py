import unittest
from mltrace import Component, set_db_uri


class TestComponents(unittest.TestCase):
    def setUp(self):
        set_db_uri("test")

    def testBasicComponent(self):
        # Create component then log a run of it
        c = Component("aditi", "test", "test_description")

        @c.run
        def function():
            foo = "foo"
            bar = "bar"
            return

        function()

    def testFunctionNoReturnVars(self):
        # Create component then log a run of it
        c = Component("aditi", "test", "test_description")

        @c.run
        def function():
            x = 0
            foo = x + 1
            bar = x + 2

        function()

    def testComponentWrongVar(self):
        # Have a var not exist in the function and assert there is
        # an error
        c = Component("aditi", "test", "test_description")

        @c.run(
            component_name="test_component",
            input_vars=["idontexist"],  # Not valid
            output_vars=["bar"],
        )
        def test_function():
            x = 0
            foo = x + 1
            bar = x + 2

        @c.run(
            component_name="test_component",
            input_vars=["foo"],
            output_vars=["barry"],  # Not valid
        )
        def test_function2():
            x = 0
            foo = x + 1
            bar = x + 2

        with self.assertRaises(ValueError):
            test_function()

        with self.assertRaises(ValueError):
            test_function2()


if __name__ == "__main__":
    unittest.main()
