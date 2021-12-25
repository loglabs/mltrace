"""
metrics.py

This file defines many common metrics for use in machine learning.
"""

from sklearn import metrics

import inspect
import typing

supported_sklearn_metric_functions = {
    "accuracy": metrics.accuracy_score,
    "precision": metrics.precision_score,
    "recall": metrics.recall_score,
    "f1": metrics.f1_score,
    "roc_auc": metrics.roc_auc_score,
    "mean_absolute_error": metrics.mean_absolute_error,
    "mean_squared_error": metrics.mean_squared_error,
    "median_absolute_error": metrics.median_absolute_error,
    "r2": metrics.r2_score,
    "explained_variance": metrics.explained_variance_score,
    "confusion_matrix": metrics.confusion_matrix,
    "mutual_info_score": metrics.mutual_info_score,
}

supported_sklearn_metrics = supported_sklearn_metric_functions.keys()


def get_metric_function(name):
    """
    Get a metric from the supported_sklearn_metric_functions dictionary.

    Parameters
    ----------
    name : str
        The name of the metric to get.

    Returns
    -------
    metric : function
        The metric function.
    """
    if name in supported_sklearn_metric_functions:
        return supported_sklearn_metric_functions[name]

    raise ValueError(
        "The metric {} is not supported. Supported metrics are: {}".format(
            name, list(supported_sklearn_metrics)
        )
    )


class Metric(object):
    def __init__(
        self,
        name: str,
        compute_freqency: int = 1,
        window_size: int = None,
        fn: typing.Callable = None,
    ):
        self.name = name
        self.compute_freqency = compute_freqency
        self.window_size = window_size

        # Create function
        self.fn = fn
        if name in supported_sklearn_metrics and not self.fn:
            self.fn = get_metric_function(name)

        if not self.fn:
            raise ValueError(
                "You must pass a supported metric name or fn yourself."
            )

        # Check the function is well formed (has y_true, y_pred signature)
        args = inspect.signature(self.fn)
        if len(args.parameters) < 2:
            raise RuntimeError(
                "The function must take at least 2 arguments: y_true, y_pred."
            )

    def getIdentifier(self):
        return (
            f"{self.name}_freq{self.compute_freqency}_window{self.window_size}"
        )
