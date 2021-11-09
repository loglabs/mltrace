import unittest
from mltrace import \
    Component, \
    set_db_uri


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

    def testComponentKWargs(self):
        # Test that logs are successful with kwargs
        c = Component("aditi", "test", "test_description")

        @c.run(
            component_name="test_component",
            input_kwargs={"inp_key": "inp_val"},
            output_kwargs={"out_key": "out_val"},
        )
        def function(inp_key, inp_val):
            out_key = "another_filename.pkl"
            out_val = [1, 2, 3, 4, 5]

        function(
            inp_key="some_filename.pkl",
            inp_val=[1, 2, 3, 4, 5],
        )

    def testComponentKWargsList(self):
        c = Component("aditi", "test", "test_description")

        @c.run(
            component_name="test_component",
            input_kwargs={"inp_key": "inp_val"},
            output_kwargs={"out_key": "out_val"},
        )
        def function(inp_key, inp_val):
            out_key = ["another_filename1.pkl", "another_filename2.pkl"]
            out_val = [1, 2]

        function(
            inp_key=["some_filename1.pkl", "some_filename2.pkl"],
            inp_val=[11, 22],
        )

    def testComponentKWargsListWrongLengths(self):
        c = Component("aditi", "test", "test_description")

        @c.run(
            component_name="test_component",
            input_kwargs={"inp_key": "inp_val"},
            output_kwargs={"out_key": "out_val"},
        )
        def function(inp_key, inp_val):
            out_key = ["another_filename1.pkl", "another_filename2.pkl"]
            out_val = 1

        with self.assertRaises(ValueError):
            function(
                inp_key=["some_filename1.pkl", "some_filename2.pkl"],
                inp_val=1,
            )

    def testComponentKWargsListWrongNames(self):
        c = Component("aditi", "test", "test_description")

        @c.run(
            component_name="test_component",
            input_kwargs={"inp_keykeykey": "inp_valvalvalval"},
            output_kwargs={"out_key": "out_val"},
        )
        def func_wrong_input(inp_key, inp_val):
            out_key = "another_filename.pkl"
            out_val = 1

        @c.run(
            component_name="test_component",
            input_kwargs={"inp_key": "inp_val"},
            output_kwargs={"out_keykeykeykey": "out_valvalvalval"},
        )
        def func_wrong_output(inp_key, inp_val):
            out_key = "another_filename.pkl"
            out_val = 1

        with self.assertRaises(ValueError):
            func_wrong_input(
                inp_key="some_filename.pkl",
                inp_val=[1],
            )

        with self.assertRaises(ValueError):
            func_wrong_output(
                inp_key="some_filename.pkl",
                inp_val=[1],
            )


if __name__ == "__main__":
    unittest.main()
