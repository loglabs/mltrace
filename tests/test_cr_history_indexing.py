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
    if crOne.start_timestamp == crTwo.start_timestamp and crOne.end_timestamp == crTwo.end_timestamp:
        return True
    return False


class TestComponentRunHistory(unittest.TestCase):
    def setUp(self):
        set_db_uri("test")
        self.new_component = TestHistoryComponent("history_test_six", "boyuan")

        @self.new_component.run(auto_log=True)
        def function(num):
            num += 2
            return num ** 2

        # initialize four component run for TestHistoryComponent
        for i in range (0, 4):
            function(i)

        self.historyLength = len(self.new_component.history)
        self.firstComponentRun = self.new_component.history.get_runs_by_index(0, 1)
        self.lastComponentRun = self.new_component.history.get_runs_by_index(self.historyLength - 1, self.historyLength)[0]
        self.secondAndThirdComponentRun = self.new_component.history.get_runs_by_index(1, 3)

    def testPstPstIndex(self):

        # case 1: (0, 0) return zero componentRun
        resCrList = self.new_component.history.get_runs_by_index(0, 0)
        self.assertEqual(len(resCrList), 0)

        # case 2: (0, 1) return the first componentRun
        resCrList = self.new_component.history.get_runs_by_index(0, 1)
        self.assertEqual(len(resCrList), 1)
        self.assertTrue(isEqualComponentRun(resCrList[0], self.firstComponentRun))

        # case 3: (len(componentRun) - 1, len(componentRun)) return the last componentRun
        resCrList = self.new_component.history.get_runs_by_index(self.historyLength - 1, self.historyLength)
        self.assertEqual(len(resCrList), 1)
        self.assertEqual(isEqualComponentRun(resCrList[0], self.lastComponentRun))

        # case 4: (1, 3) return the second and third componentRun given len(componentRun) >=3)
        resCrList = self.new_component.history.get_runs_by_index(1, 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
            if idx >= len(self.secondAndThirdComponentRun):
                break
            else:
                self.assertEqual(isEqualComponentRun(cr, self.secondAndThirdComponentRun[idx]))


    def testPstNgtIndex(self):

        # case 1: (0, -len(componentRun) + 1) return first componentRun)
        resCrList = self.new_component.history.get_runs_by_index(0, -self.historyLength + 1)
        self.assertEqual(len(resCrList), 1)
        self.assertEqual(isEqualComponentRun(resCrList[0], self.firstComponentRun))

        # case 2: cannot retrieve last componentRun this way

        # case 3: (1, -len(componentRun) + 3) return second and third componentRun given len(componentRun) >=4)
        resCrList = self.new_component.history.get_runs_by_index(1, -self.historyLength + 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
             self.assertEqual(isEqualComponentRun(cr, self.secondAndThirdComponentRun[idx]))

    def testNgtPstIndex(self):

        # case 1: (-len(componentRun), 1) return the first componentRun)
        resCrList = self.new_component.history.get_runs_by_index(-self.historyLength, 1)
        self.assertEqual(len(resCrList), 1)
        self.assertEqual(isEqualComponentRun(resCrList[0], self.firstComponentRun))

        # case 2: (-1, len(componentRun)) return the last componentRun)
        resCrList = self.new_component.history.get_runs_by_index(-1, self.historyLength)
        self.assertEqual(len(resCrList),)
        self.assertEqual(isEqualComponentRun(resCrList[0], self.lastComponentRun))

        # case 3: (-len(componentRun) + 1, 3) return second and third componentRun given len(componentRun) >=3)
        resCrList = self.new_component.history.get_runs_by_index(-self.historyLength + 1, 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
             self.assertEqual(isEqualComponentRun(cr, self.secondAndThirdComponentRun[idx]))


    def testNgtNgtIndex(self):

        # case 1: (-len(componentRun), -len(componentRun) + 1) return first componentRun)
        resCrList = self.new_component.history.get_runs_by_index(-self.historyLength, -self.historyLength + 1)
        self.assertEqual(len(resCrList), 1)
        self.assertEqual(isEqualComponentRun(resCrList[0], self.firstComponentRun))

        # case 2: cannot retrieve last componentRun this way

        # case 3: (-len(componentRun) + 1, -len(componentRun) + 3) return second and third componentRun given len(componentRun) >=4)
        resCrList = self.new_component.history.get_runs_by_index(-self.historyLength + 1, -self.historyLength + 3)
        self.assertEqual(len(resCrList), 2)
        for idx, cr in enumerate(resCrList):
             self.assertEqual(isEqualComponentRun(cr, self.secondAndThirdComponentRun[idx]))