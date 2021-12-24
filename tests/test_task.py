from mltrace import Task, supported_sklearn_metrics

import random
import string
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

    def testComputeMettrics(self):
        task = Task("test_metrics")
        for _ in range(10):
            output_id = "".join(
                random.choice(string.ascii_uppercase) for _ in range(10)
            )
            task.logOutput(random.randint(0, 1), output_id)
            task.logFeedback(random.randint(0, 1), output_id)

        for metric in supported_sklearn_metrics:
            task.computeMetric(metric)
