from mltrace import Component
import unittest
from mltrace import (
    set_db_uri,
)
from mltrace.db import Store


class TestHistoryComponent(Component):
    def __init__(
        self,
        name="",
        owner="",
        description="",
        beforeTests=[],
        afterTests=[],
        tags=[],
    ):
        super().__init__(
            name, owner, description, beforeTests, afterTests, tags)


def isEqualComponentRun(crOne, crTwo):
    if crOne.start_timestamp == crTwo.start_timestamp \
            and crOne.end_timestamp == crTwo.end_timestamp:
        return True
    return False


class TestComponentRunHistory(unittest.TestCase):
    def setUp(self):
        self.store = Store("test")

        # initialize four component run for TestHistoryComponent
        self.store.create_component("mock_component", "", "")
        num_runs = 4
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

        self.historyLength = self.store.get_component_runs_count(
            "mock_component")
        self.firstComponentRun = self.store.get_component_runs_by_index(
            "mock_component", 0, 1)[0]
        self.lastComponentRun = self.store.get_component_runs_by_index(
            "mock_component", self.historyLength - 1, self.historyLength)[0]
        self.secondAndThirdComponentRun = \
            self.store.get_component_runs_by_index(
                "mock_component", 1, 3)

    """ 
    Test all possible queries: 
        get_component_runs_by_index(positive idx, positive idx)
    """
    def testPstPstIndex(self):

        # case 1: (0, 0) return zero componentRun
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", 0, 0)
        self.assertEqual(len(resCrList), 0)

        # case 2: (0, 1) return the first componentRun
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", 0, 1)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(
            resCrList[0], self.firstComponentRun))

        # case 3: (len(componentRun) - 1, len(componentRun))
        # return the last componentRun
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", self.historyLength - 1, self.historyLength)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(
            resCrList[0], self.lastComponentRun))

        # case 4: (1, 3) return the second and third componentRun
        # given len(componentRun) >=3)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", 1, 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
            if idx >= len(self.secondAndThirdComponentRun):
                break
            else:
                self.assertTrue(isEqualComponentRun(
                    cr, self.secondAndThirdComponentRun[idx]))

    """ 
    Test all possible queries: 
        get_component_runs_by_index(positive idx, negative idx)
    """
    def testPstNgtIndex(self):

        # case 1: (0, -len(componentRun) + 1) return first componentRun)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", 0, -self.historyLength + 1)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(
            resCrList[0], self.firstComponentRun))

        # case 2: cannot retrieve last componentRun this way

        # case 3: (1, -len(componentRun) + 3) return second and
        # third componentRun given len(componentRun) >=4)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", 1, -self.historyLength + 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
            self.assertTrue(isEqualComponentRun(
                cr, self.secondAndThirdComponentRun[idx]))

    """ 
    Test all possible queries: 
        get_component_runs_by_index(negative idx, positive idx)
    """
    def testNgtPstIndex(self):

        # case 1: (-len(componentRun), 1) return the first componentRun)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", -self.historyLength, 1)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(
            resCrList[0], self.firstComponentRun))

        # case 2: (-1, len(componentRun)) return the last componentRun)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", -1, self.historyLength)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(
            resCrList[0], self.lastComponentRun))

        # case 3: (-len(componentRun) + 1, 3) return second
        # and third componentRun given len(componentRun) >=3)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", -self.historyLength + 1, 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
            self.assertTrue(isEqualComponentRun(
                cr, self.secondAndThirdComponentRun[idx]))

    """ 
    Test all possible queries: 
        get_component_runs_by_index(negative idx, negative idx)
    """
    def testNgtNgtIndex(self):

        # case 1: (-len(componentRun), -len(componentRun) + 1)
        # return first componentRun)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", -self.historyLength, -self.historyLength + 1)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(
            resCrList[0], self.firstComponentRun))

        # case 2: cannot retrieve last componentRun this way

        # case 3: (-len(componentRun) + 1, -len(componentRun) + 3)
        # return second and third componentRun given len(componentRun) >=4)
        resCrList = self.store.get_component_runs_by_index(
            "mock_component", -self.historyLength + 1, -self.historyLength + 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
            self.assertTrue(isEqualComponentRun(
                cr, self.secondAndThirdComponentRun[idx]))
