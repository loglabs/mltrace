import copy
import unittest

from mltrace.db import Component, ComponentRun, IOPointer, Store


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = Store("test")

    def testComponent(self):
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )
        component = self.store.get_component("test_component")
        self.assertEqual(component.name, "test_component")

        # Retrieve components with owner
        components = self.store.get_components_with_owner("shreya")
        self.assertEqual(1, len(components))

    def testCompleteComponentRun(self):
        # Create component
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )

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
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )

        # Create incomplete component run
        cr = self.store.initialize_empty_component_run("test_component")
        with self.assertRaises(RuntimeError):
            self.store.commit_component_run(cr)

    def testTags(self):
        # Create component without tags
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )

        # Add tags
        self.store.add_tags_to_component("test_component", ["tag1", "tag2"])

        # Test retrieval
        component = self.store.get_component("test_component")
        tags = [t.name for t in component.tags]
        self.assertEqual(component.name, "test_component")
        self.assertEqual(set(tags), set(["tag1", "tag2"]))

    def testDuplicateTags(self):
        # Create component without tags
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )

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
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )
        for idx in range(2):
            cr = self.store.initialize_empty_component_run("test_component")
            cr.set_start_timestamp()
            cr.set_end_timestamp()
            cr.add_input(inp)
            cr.add_output(out)
            self.store.commit_component_run(cr)

        # Create another two component runs that have the same output
        self.store.create_component(
            "test_component", "test_description", "shreya"
        )
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

    def _set_up_computation(self):
        # Create dag of computation
        # Create component and IOPointers
        for i in range(1, 5):
            self.store.create_component(
                f"test_component_{i}", "test_description", "shreya"
            )

        iop = [self.store.get_io_pointer(f"iop_{i}") for i in range(1, 5)]

        # Create component runs
        cr1 = self.store.initialize_empty_component_run("test_component_1")
        cr1.set_start_timestamp()
        cr1.set_end_timestamp()
        cr1.add_output(iop[0])
        self.store.set_dependencies_from_inputs(cr1)
        self.store.commit_component_run(cr1)

        cr2 = self.store.initialize_empty_component_run("test_component_2")
        cr2.set_start_timestamp()
        cr2.set_end_timestamp()
        cr2.add_output(iop[0])
        self.store.set_dependencies_from_inputs(cr2)
        self.store.commit_component_run(cr2)

        cr3 = self.store.initialize_empty_component_run("test_component_3")
        cr3.set_start_timestamp()
        cr3.set_end_timestamp()
        cr3.add_input(iop[0])
        cr3.add_outputs([iop[1], iop[2]])
        self.store.set_dependencies_from_inputs(cr3)
        self.store.commit_component_run(cr3)

        cr4 = self.store.initialize_empty_component_run("test_component_4")
        cr4.set_start_timestamp()
        cr4.set_end_timestamp()
        cr4.add_input(iop[2])
        cr4.add_output(iop[3])
        self.store.set_dependencies_from_inputs(cr4)
        self.store.commit_component_run(cr4)

    def testTrace(self):
        self._set_up_computation()

        # Call trace functionality
        trace = self.store.trace("iop_4")
        level_id = [(level, cr.id) for level, cr in trace]

        self.assertEqual(level_id, [(0, 4), (1, 3), (2, 2)])

    def testEmptyTrace(self):
        with self.assertRaises(RuntimeError):
            self.store.trace("some_weird_pointer")
        with self.assertRaises(RuntimeError):
            self.store.web_trace("some_weird_pointer")

    def testWebTrace(self):
        self._set_up_computation()

        # Call web trace functionality. The ordering is nondeterministic.
        expected_res = [
            {
                "id": "componentrun_4",
                "label": "test_component_4",
                "hasCaret": True,
                "isExpanded": True,
                "stale": [],
                "childNodes": [
                    {
                        "id": "iopointer_iop_4",
                        "label": "iop_4",
                        "hasCaret": False,
                        "parent": "componentrun_4",
                    },
                    {
                        "id": "componentrun_3",
                        "label": "test_component_3",
                        "hasCaret": True,
                        "isExpanded": True,
                        "stale": [],
                        "childNodes": [
                            {
                                "id": "iopointer_iop_2",
                                "label": "iop_2",
                                "hasCaret": False,
                                "parent": "componentrun_3",
                            },
                            {
                                "id": "iopointer_iop_3",
                                "label": "iop_3",
                                "hasCaret": False,
                                "parent": "componentrun_3",
                            },
                            {
                                "id": "componentrun_2",
                                "label": "test_component_2",
                                "hasCaret": True,
                                "isExpanded": True,
                                "stale": [],
                                "childNodes": [
                                    {
                                        "id": "iopointer_iop_1",
                                        "label": "iop_1",
                                        "hasCaret": False,
                                        "parent": "componentrun_2",
                                    }
                                ],
                            },
                        ],
                    },
                ],
            }
        ]
        web_trace = self.store.web_trace("iop_4")

        self.assertEqual(web_trace, expected_res)

    def testBasicFlaggedOutputs(self):
        # Create components and iopointers
        self.store.create_component(
            "test_component_A", "test_description", "shreya"
        )
        self.store.create_component(
            "test_component_B", "test_description", "shreya"
        )

        iop = [self.store.get_io_pointer(f"iop_{i}") for i in range(1, 5)]

        # Create component runs
        # First pipeline
        cr_A1 = self.store.initialize_empty_component_run("test_component_A")
        cr_A1.set_start_timestamp()
        cr_A1.set_end_timestamp()
        cr_A1.add_outputs([iop[0], iop[1]])
        self.store.set_dependencies_from_inputs(cr_A1)
        self.store.commit_component_run(cr_A1)
        cr_B1 = self.store.initialize_empty_component_run("test_component_B")
        cr_B1.set_start_timestamp()
        cr_B1.set_end_timestamp()
        cr_B1.add_input(iop[0])
        cr_B1.add_output(iop[2])
        self.store.set_dependencies_from_inputs(cr_B1)
        self.store.commit_component_run(cr_B1)
        # Second pipeline, which builds off iop2
        cr_B2 = self.store.initialize_empty_component_run("test_component_B")
        cr_B2.set_start_timestamp()
        cr_B2.set_end_timestamp()
        cr_B2.add_input(iop[1])
        cr_B2.add_output(iop[3])
        self.store.set_dependencies_from_inputs(cr_B2)
        self.store.commit_component_run(cr_B2)

        # Flag iop_3 and iop_4
        self.store.set_io_pointer_flag("iop_3", True)
        self.store.set_io_pointer_flag("iop_4", True)

        # Run diagnose. It should output
        # [component_A, component_B, component_B]'s corresponding run IDs
        _, res = self.store.diagnose_flagged_outputs()
        res = [(cr.id, count) for cr, count in res]
        expected_res = [(1, 2), (3, 1), (2, 1)]
        self.assertEqual(res, expected_res)

    def testManyFlaggedOutputs(self):
        # Create components and iopointers
        self.store.create_component(
            "test_component_A", "test_description", "shreya"
        )
        self.store.create_component(
            "test_component_B", "test_description", "shreya"
        )
        self.store.create_component(
            "test_component_C", "test_description", "shreya"
        )

        iop = [self.store.get_io_pointer(f"iop_{i}") for i in range(1, 8)]
        # Create component runs
        # First pipeline
        cr_A1 = self.store.initialize_empty_component_run("test_component_A")
        cr_A1.set_start_timestamp()
        cr_A1.set_end_timestamp()
        cr_A1.add_outputs([iop[0], iop[1]])
        self.store.set_dependencies_from_inputs(cr_A1)
        self.store.commit_component_run(cr_A1)
        cr_B1 = self.store.initialize_empty_component_run("test_component_B")
        cr_B1.set_start_timestamp()
        cr_B1.set_end_timestamp()
        cr_B1.add_input(iop[0])
        cr_B1.add_output(iop[2])
        self.store.set_dependencies_from_inputs(cr_B1)
        self.store.commit_component_run(cr_B1)
        cr_C1 = self.store.initialize_empty_component_run("test_component_C")
        cr_C1.set_start_timestamp()
        cr_C1.set_end_timestamp()
        cr_C1.add_inputs([iop[1], iop[2]])
        cr_C1.add_output(iop[3])
        self.store.set_dependencies_from_inputs(cr_C1)
        self.store.commit_component_run(cr_C1)

        # Second pipeline
        cr_C2 = self.store.initialize_empty_component_run("test_component_C")
        cr_C2.set_start_timestamp()
        cr_C2.set_end_timestamp()
        cr_C2.add_inputs([iop[1], iop[2]])
        cr_C2.add_output(iop[4])
        self.store.set_dependencies_from_inputs(cr_C2)
        self.store.commit_component_run(cr_C2)

        # Third pipeline
        cr_C3 = self.store.initialize_empty_component_run("test_component_C")
        cr_C3.set_start_timestamp()
        cr_C3.set_end_timestamp()
        cr_C3.add_inputs([iop[1], iop[2]])
        cr_C3.add_output(iop[5])
        self.store.set_dependencies_from_inputs(cr_C3)
        self.store.commit_component_run(cr_C3)

        # Fourth pipeline
        cr_C4 = self.store.initialize_empty_component_run("test_component_C")
        cr_C4.set_start_timestamp()
        cr_C4.set_end_timestamp()
        cr_C4.add_inputs([iop[1], iop[2]])
        cr_C4.add_output(iop[6])
        self.store.set_dependencies_from_inputs(cr_C4)
        self.store.commit_component_run(cr_C4)

        # Flag
        self.store.set_io_pointer_flag("iop_4", True)
        self.store.set_io_pointer_flag("iop_5", True)
        self.store.set_io_pointer_flag("iop_6", True)
        self.store.set_io_pointer_flag("iop_7", True)

        _, res = self.store.review_flagged_outputs()
        res = [(cr.component_name, cr.id, count) for cr, count in res]
        expected_res = [
            ("test_component_B", 2, 4),
            ("test_component_A", 1, 4),
            ("test_component_C", 6, 1),
            ("test_component_C", 5, 1),
            ("test_component_C", 4, 1),
            ("test_component_C", 3, 1),
        ]
        self.assertEqual(res, expected_res)


if __name__ == "__main__":
    unittest.main()
