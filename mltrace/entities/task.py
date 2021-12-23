from mltrace import utils as clientUtils
from mltrace.db import Store

import typing


class Task(object):
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.store = Store(clientUtils.get_db_uri())
        # TODO(shreyashankar): Add metric cache

    def logOutput(
        self,
        output_value: float,
        identifier: str,
    ):
        self.store.log_output(
            identifier=identifier,
            task_name=self.task_name,
            val=output_value,
        )

    def logFeedback(
        self,
        feedback_value: float,
        identifier: str,
    ):
        self.store.log_feedback(
            identifier=identifier,
            task_name=self.task_name,
            val=feedback_value,
        )

    def getOutputs(self, limit: int = None, window_size: int = None):
        return self.store.get_outputs_or_feedback(
            self.task_name,
            tablename="output_table",
            limit=limit,
            window_size=window_size,
        )

    def getFeedback(self, limit: int = None, window_size: int = None):
        return self.store.get_outputs_or_feedback(
            self.task_name,
            tablename="feedback_table",
            limit=limit,
            window_size=window_size,
        )

    def computeMetric(
        self,
        metric_fn,
        window_size: int = None,
    ):
        return self.store.compute_metric(
            metric_fn, self.task_name, window_size=window_size
        )
