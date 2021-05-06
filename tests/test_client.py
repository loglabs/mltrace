import copy
import unittest
import warnings

from datetime import datetime
from mltrace import (
    set_db_uri,
    create_component,
    log_component_run,
    register,
    get_history,
    get_recent_run_ids,
)
from mltrace.entities import ComponentRun


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

    def testRegister(self):
        # Create component then log a run of it
        create_component("test_component", "test_description", "shreya")

        @register(
            component_name="test_component", input_vars=["foo"], output_vars=["bar"]
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
            component_name="test_component", input_vars=["foo"], output_vars=["bar"]
        )
        def test_func():
            x = 0
            foo = x + 1
            bar = x + 2

        test_func()


if __name__ == "__main__":
    unittest.main()
