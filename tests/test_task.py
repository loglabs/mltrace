from mltrace import Task

import unittest


class TestTask(unittest.TestCase):
    def testLogOutput(self):
        task = Task("test_output")
        task.logOutput(1, "ABC")
        res = task.getOutputs()
        self.assertTrue(float(res[0][2]) == 1.0)

    def testLogFeedback(self):
        task = Task("test_feedback")
        task.logFeedback(1, "ABC")
        res = task.getFeedback()
        self.assertTrue(float(res[0][2]) == 1.0)
        self.assertTrue(len(task.getOutputs()) == 0)

    def testComputeMSE(self):
        task = Task("test_mse")
        task.logOutput(0.5, "ABC")
        task.logFeedback(1, "ABC")

        def mse(y_true, y_pred):
            ret = 0.0

            for i in range(len(y_true)):
                ret += (y_true[i] - y_pred[i]) ** 2

            return ret ** 0.5

        self.assertTrue(task.computeMetric(mse) == 0.5)

    def testComputeBadFunction(self):
        task = Task("test_bad_function")
        task.logOutput(0.5, "ABC")
        task.logFeedback(1, "ABC")

        def bad(onearg):
            pass

        with self.assertRaises(RuntimeError):
            task.computeMetric(bad)
