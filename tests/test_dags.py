import copy
import unittest

from mltrace.db import Component, ComponentRun, IOPointer, Store


class TestDags(unittest.TestCase):
    def setUp(self):
        self.store = Store("test")

    def testLinkedList(self):
        # Create chain of component runs
        expected_result = []
        num_runs = 10
        for i in range(1, num_runs + 1):
            self.store.create_component(f"mock_component_{i}", "", "")
            inp = self.store.get_io_pointer(f"iop_{i}")
            out = self.store.get_io_pointer(f"iop_{i + 1}")
            cr = self.store.initialize_empty_component_run(f"mock_component_{i}")
            cr.set_start_timestamp()
            cr.set_end_timestamp()
            cr.add_input(inp)
            cr.add_output(out)
            self.store.set_dependencies_from_inputs(cr)
            self.store.commit_component_run(cr)
            expected_result.append((num_runs - i, i))

        # Reverse the expected result
        expected_result.reverse()

        # Trace the final output
        trace = self.store.trace("iop_11")
        level_id = [(l, cr.id) for l, cr in trace]
        self.assertEqual(expected_result, level_id)

    def testVersionedComputation(self):
        # Run the same computation many times
        self.store.create_component("mock_component", "", "")
        num_runs = 10
        for i in range(1, num_runs + 1):
            inp = self.store.get_io_pointer("inp")
            out = self.store.get_io_pointer("out")
            cr = self.store.initialize_empty_component_run("mock_component")
            cr.set_start_timestamp()
            cr.set_end_timestamp()
            cr.add_input(inp)
            cr.add_output(out)
            self.store.set_dependencies_from_inputs(cr)
            self.store.commit_component_run(cr)

        # Trace the out pointer. Only most recent run ID should show.
        trace = self.store.trace("out")
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0][0], 0)
        self.assertEqual(trace[0][1].id, num_runs)

    def testTree(self):
        # Create a tree of component runs, 5 levels deep
        num_levels = 2
        global cr_counter
        global iop_counter
        cr_counter = 1
        iop_counter = 1

        def create_tree(level, inp):
            if level == num_levels:
                return

            global cr_counter
            global iop_counter

            self.store.create_component(f"mock_component_{cr_counter}", "", "")
            cr = self.store.initialize_empty_component_run(
                f"mock_component_{cr_counter}"
            )
            cr_counter += 1
            cr.set_start_timestamp()
            cr.set_end_timestamp()

            # Create output pointers
            out1 = self.store.get_io_pointer(f"iop_{iop_counter}")
            iop_counter += 1
            out2 = self.store.get_io_pointer(f"iop_{iop_counter}")
            iop_counter += 1

            # Add and commit component run
            cr.add_input(inp)
            cr.add_outputs([out1, out2])
            self.store.set_dependencies_from_inputs(cr)
            self.store.commit_component_run(cr)

            # Create left and right trees
            create_tree(level + 1, out1)
            create_tree(level + 1, out2)

        # Create first input pointer and tree of computation
        inp = self.store.get_io_pointer(f"iop_{iop_counter}")
        iop_counter += 1
        create_tree(0, inp)

        # Grab last iop id and trace it
        last_iop_id = f"iop_{iop_counter - 1}"
        trace = self.store.trace(last_iop_id)
        level_id = [(l, cr.id) for l, cr in trace]
        self.assertEqual(level_id, [(0, 3), (1, 1)])

    def testCycle(self):
        # Create cycle. Since dependencies are versioned, we shouldn't run into problems.
        # Create io pointers and components
        iop1 = self.store.get_io_pointer("iop1")
        iop2 = self.store.get_io_pointer("iop2")
        self.store.create_component("component_1", "", "")
        self.store.create_component("component_2", "", "")

        # Create component runs
        cr = self.store.initialize_empty_component_run("component_1")
        cr.set_start_timestamp()
        cr.set_end_timestamp()
        cr.add_input(iop1)
        cr.add_output(iop2)
        self.store.set_dependencies_from_inputs(cr)
        self.store.commit_component_run(cr)

        cr = self.store.initialize_empty_component_run("component_2")
        cr.set_start_timestamp()
        cr.set_end_timestamp()
        cr.add_input(iop2)
        cr.add_output(iop1)
        self.store.set_dependencies_from_inputs(cr)
        self.store.commit_component_run(cr)

        # Trace iop1
        trace_1 = [(l, cr.id) for l, cr in self.store.trace("iop1")]
        trace_2 = [(l, cr.id) for l, cr in self.store.trace("iop2")]
        self.assertEqual(trace_1, [(0, 2), (1, 1)])
        self.assertEqual(trace_2, [(0, 1)])


if __name__ == "__main__":
    unittest.main()