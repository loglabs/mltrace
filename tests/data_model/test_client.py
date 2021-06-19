import copy
import unittest

from mltrace.entities import Component, ComponentRun, IOPointer


class TestComponent(unittest.TestCase):
    def setUp(self):
        self.mock_component = Component(
            "mock_component", "mock component 2", "shreya", ["mock_tag"]
        )

        self.mock_component_dict = {
            "name": self.mock_component.name,
            "description": self.mock_component.description,
            "owner": self.mock_component.owner,
            "tags": self.mock_component.tags,
        }

    def testSerialize(self):
        """
        Test the serialization functionality.
        """
        mock_component_dict = self.mock_component.to_dictionary()
        self.assertEqual(mock_component_dict, self.mock_component_dict)

    def testChangeProperty(self):
        """
        Test changing a property. Should return an error.
        """
        mock_component_copy = copy.deepcopy(self.mock_component)

        with self.assertRaises(AttributeError):
            mock_component_copy.name = "changed_name"


class TestComponentRun(unittest.TestCase):
    def setUp(self):
        self.mock_component_run = ComponentRun("mock_component_run")
        self.mock_component_run_dict = {
            "component_name": "mock_component_run",
            "notes": "",
            "inputs": [],
            "outputs": [],
            "git_hash": None,
            "git_tags": [],
            "code_snapshot": None,
            "start_timestamp": None,
            "end_timestamp": None,
            "dependencies": [],
            "id": None,
            "stale": [],
        }

        self.mock_inputs = [
            IOPointer("mock_input_1"),
            IOPointer("mock_input_2"),
        ]
        self.mock_outputs = [
            IOPointer("mock_output_1"),
            IOPointer("mock_output_2"),
        ]

    def testSerialize(self):
        """
        Test the serialization functionality.
        """
        self.assertEqual(
            self.mock_component_run.to_dictionary(),
            self.mock_component_run_dict,
        )

    def testSetStartEndError(self):
        """
        Test that setting start and end ts as non
        datetime types throws an error.
        """

        with self.assertRaises(TypeError):
            self.mock_component_run.set_start_timestamp("incorrect_type")

        with self.assertRaises(TypeError):
            self.mock_component_run.set_end_timestamp("incorrect_type")

    def testAddInputOutput(self):
        cr = copy.deepcopy(self.mock_component_run)
        for inp in self.mock_inputs:
            cr.add_input(inp)
        for out in self.mock_outputs:
            cr.add_output(out)

        self.assertEqual(cr.inputs, list(set(self.mock_inputs)))
        self.assertEqual(cr.outputs, list(set(self.mock_outputs)))

    def testAddInputsOutputs(self):
        cr = copy.deepcopy(self.mock_component_run)
        cr.add_inputs(self.mock_inputs)
        cr.add_outputs(self.mock_outputs)

        self.assertEqual(cr.inputs, list(set(self.mock_inputs)))
        self.assertEqual(cr.outputs, list(set(self.mock_outputs)))

    def testAddDuplicateInputs(self):
        cr = copy.deepcopy(self.mock_component_run)
        cr.add_inputs(self.mock_inputs)
        cr.add_inputs(self.mock_inputs)

        self.assertEqual(cr.inputs, list(set(self.mock_inputs)))

    def testAddNotes(self):
        cr = copy.deepcopy(self.mock_component_run)
        expected_output = "this is a test note"
        cr.notes = "this is a test note"

        self.assertEqual(cr.notes, expected_output)

    def testAddNotesError(self):
        """
        Test that adding non-str input to the notes attribute
        gives a TypeError
        """
        with self.assertRaises(TypeError):
            self.mock_component_run.notes = ["incorrect_type"]


if __name__ == "__main__":
    unittest.main()
