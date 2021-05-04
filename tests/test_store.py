import copy
import unittest

from datetime import datetime
from mltrace.db import Component, ComponentRun, IOPointer, Store


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = Store("test", test=True)

    def testComponent(self):
        self.store.create_component("test_component", "test_description", "shreya")
        component = self.store.get_component("test_component")
        self.assertEqual(component.name, "test_component")

        # Retrieve components with owner
        components = self.store.get_components_with_owner("shreya")
        self.assertEqual(1, len(components))

    def testCompleteComponentRun(self):
        # Create component
        self.store.create_component("test_component", "test_description", "shreya")

        # Create component run
        cr = self.store.initialize_empty_component_run("test_component")
        cr.set_start_timestamp()
        cr.set_end_timestamp()
        cr.add_input(IOPointer("inp"))
        cr.add_output(IOPointer("out"))
        self.store.commit_component_run(cr)

        # Test retrieval
        component_runs = self.store.get_history("test_component", limit=None)
        self.assertEqual(1, len(component_runs))
        self.assertEqual(component_runs[0], cr)

    def testIncompleteComponentRun(self):
        # Create component
        self.store.create_component("test_component", "test_description", "shreya")

        # Create incomplete component run
        cr = self.store.initialize_empty_component_run("test_component")
        with self.assertRaises(RuntimeError):
            self.store.commit_component_run(cr)

    def testTags(self):
        # Create component without tags
        self.store.create_component("test_component", "test_description", "shreya")

        # Add tags
        self.store.add_tags_to_component("test_component", ["tag1", "tag2"])

        # Test retrieval
        component = self.store.get_component("test_component")
        tags = [t.name for t in component.tags]
        self.assertEqual(component.name, "test_component")
        self.assertEqual(set(tags), set(["tag1", "tag2"]))

    def testDuplicateTags(self):
        # Create component without tags
        self.store.create_component("test_component", "test_description", "shreya")

        # Add duplicate tags
        self.store.add_tags_to_component("test_component", ["tag1", "tag1"])

        # Test retrieval
        component = self.store.get_component("test_component")
        tags = [t.name for t in component.tags]
        self.assertEqual(component.name, "test_component")
        self.assertEqual(tags, ["tag1"])

    def testIOPointer(self):
        # Test there is no IOPointer
        with self.assertRaises(RuntimeError):
            self.store.get_io_pointer("iop", create=False)

        # Create IOPointer
        iop = self.store.get_io_pointer("iop")
        iop2 = self.store.get_io_pointer("iop")

        self.assertEqual(iop, iop2)

    def testIOPointers(self):
        # Create new IOPointers from scratch
        iop_names = [f"iop_{i}" for i in range(100)]
        iops = self.store.get_io_pointers(iop_names)
        iops2 = self.store.get_io_pointers(iop_names)

        self.assertEqual(set(iops), set(iops2))

    def testSetDependenciesFromInputs(self):
        # Create IO pointers
        inp = self.store.get_io_pointer("inp")
        out = self.store.get_io_pointer("out")
        another_out = self.store.get_io_pointer("another_out")

        # Create two component runs that have the same output
        self.store.create_component("test_component", "test_description", "shreya")
        for idx in range(2):
            cr = self.store.initialize_empty_component_run("test_component")
            cr.set_start_timestamp()
            cr.set_end_timestamp()
            cr.add_input(inp)
            cr.add_output(out)
            self.store.commit_component_run(cr)

        # Create another two component runs that have the same output
        self.store.create_component("test_component", "test_description", "shreya")
        for idx in range(2):
            cr = self.store.initialize_empty_component_run("test_component")
            cr.set_start_timestamp()
            cr.set_end_timestamp()
            cr.add_input(inp)
            cr.add_output(another_out)
            self.store.commit_component_run(cr)

        # Create new component run that depends on "out" pointer
        cr = self.store.initialize_empty_component_run("test_component")
        cr.set_start_timestamp()
        cr.set_end_timestamp()
        cr.add_inputs([out, another_out])
        self.store.set_dependencies_from_inputs(cr)
        self.store.commit_component_run(cr)

        # Retrieve latest component run and check dependencies
        component_runs = self.store.get_history("test_component", limit=None)
        self.assertTrue(component_runs[1] in component_runs[0].dependencies)
        self.assertTrue(component_runs[3] in component_runs[0].dependencies)

    def testTrace(self):
        pass

    def testWebTrace(self):
        pass


if __name__ == "__main__":
    unittest.main()
