import copy
import unittest

from mltrace.db import Component, ComponentRun, IOPointer, Tag


class TestComponentRun(unittest.TestCase):
    def setUp(self):
        self.mock_component_run = ComponentRun("mock")

    def testCompletenessWithNoInfo(self):
        status = self.mock_component_run.check_completeness()
        self.assertFalse(status["success"])

    def testCompletenessWithStartEnd(self):
        cr = copy.deepcopy(self.mock_component_run)
        cr.set_start_timestamp()
        cr.set_end_timestamp()

        status = cr.check_completeness()
        self.assertTrue(status["success"])

        # Assert that there are warning statements
        # because of no I/O or dependencies
        msg = status["msg"]
        self.assertTrue(len(msg) > 0)

    def testCompletenessWithStartEndDeps(self):
        cr = copy.deepcopy(self.mock_component_run)
        cr.set_start_timestamp()
        cr.set_end_timestamp()

        # Add I/O and dependencies
        cr.add_input(IOPointer("input"))
        cr.add_output(IOPointer("output"))
        cr.set_upstream(ComponentRun("another_component"))

        status = cr.check_completeness()
        self.assertTrue(status["success"])

        # Assert that there no warning statements
        msg = status["msg"]
        self.assertTrue(len(msg) == 0)


if __name__ == "__main__":
    unittest.main()
