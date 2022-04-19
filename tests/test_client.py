import copy
import unittest
import warnings

from datetime import datetime
from mltrace import (
    set_db_uri,
    create_component,
    log_component_run,
    register,
    load,
    save,
)
from mltrace.entities import ComponentRun, IOPointer


class TestClient(unittest.TestCase):
    def setUp(self):
        set_db_uri("test")

    def testLogEmptyComponentRun(self):
        # Create component then log a run of it
        create_component("test_component", "test_description", "shreya")

        # Create a ComponentRun
        cr = ComponentRun("test_component")

        with self.assertRaises(RuntimeError):
            log_component_run(cr)

    def testLogBasicComponentRun(self):
        # Create component then log a run of it
        create_component("test_component", "test_description", "shreya")

        # Create a ComponentRun
        cr = ComponentRun(component_name="test_component")
        cr.set_start_timestamp()
        cr.code_snapshot = b"def main(): return"
        cr.add_inputs(["duplicate_input", "duplicate_input"])
        cr.add_outputs(["duplicate_output", "duplicate_output"])
        cr.set_end_timestamp()

        # Log component run
        log_component_run(cr)

    def testLogKVComponentRun(self):
        # Tests implementation of values in iopointer
        create_component(
            name="valtest",
            description="Tests implementation of values in iopointer.",
            owner="me",
        )

        iop1 = ["this", "is", "the", "first"]
        iop2 = ["this", "is", "the", "second"]

        # Create iopointers and CR
        iop1 = IOPointer(name="iop1", value=iop1)
        iop2 = IOPointer(name="iop2", value=iop2)

        cr = ComponentRun("valtest")
        cr.set_start_timestamp()
        cr.set_end_timestamp()
        cr.add_input(iop1)
        cr.add_output(iop2)
        log_component_run(cr)

    def testRegister(self):
        # Create component then log a run of it
        create_component("test_component", "test_description", "shreya")

        @register(
            component_name="test_component",
            input_vars=["foo"],
            output_vars=["bar"],
        )
        def test_func():
            foo = "foo"
            bar = "bar"
            return

        test_func()

    def testRegisterNoReturn(self):
        # Create component then log a run of it
        create_component("test_component", "test_description", "shreya")

        @register(
            component_name="test_component",
            input_vars=["foo"],
            output_vars=["bar"],
        )
        def test_func():
            x = 0
            foo = x + 1
            bar = x + 2

        test_func()

    def testRegisterWrongVar(self):
        # Have a var not exist in the function and assert there is
        # an error
        create_component("test_component", "test_description", "shreya")

        @register(
            component_name="test_component",
            input_vars=["foory"],  # Not valid
            output_vars=["bar"],
        )
        def test_func():
            x = 0
            foo = x + 1
            bar = x + 2

        @register(
            component_name="test_component",
            input_vars=["foo"],
            output_vars=["barry"],  # Not valid
        )
        def test_func2():
            x = 0
            foo = x + 1
            bar = x + 2

        with self.assertRaises(ValueError):
            test_func()

        with self.assertRaises(ValueError):
            test_func2()

    def testSaveAndLoad(self):
        obj = {"foo": "bar"}
        pathname = save(obj)
        self.assertEqual(obj, load(pathname))


if __name__ == "__main__":
    unittest.main()
