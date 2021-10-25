import unittest
from mltrace.entities import components


class TestComponents(unittest.TestCase):

    def testLogEmptyComponentRun(self):
        # Create component then log a run of it
        c = components.PreprocessingComponent("aditi", "tests output for outliers")

        # Create a ComponentRun
        cr = ComponentRun("test_component")

        with self.assertRaises(RuntimeError):
            log_component_run(cr)