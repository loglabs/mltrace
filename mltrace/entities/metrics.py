"""
metrics.py

This file defines many common metrics for use in machine learning.
"""

from sklearn import metrics

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
