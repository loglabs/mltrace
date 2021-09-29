"""
This file defines different kinds of components and the corresponding tests for before and afterRun.
"""
from mltrace.base_component import Component
from mltrace.tests import Outliers

import pandas as pd


class PreprocessingComponent(Component):

    def __init__(self, username: str, beforeTests: list = [], afterTests: list = []):
        afterTests = afterTests.append(Outliers)

        super().__init__("PreprocessingComponents", username, beforeTests, afterTests)


class TrainingComponent(Component):
    def beforeRun(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        """Checks that there is no train-test leakage."""
        intersection = train_df.merge(
            test_df, how="inner", on=train_df.columns.to_list()
        )
        if not intersection.empty:
            raise Exception("There is train-test leakage!")

    def afterRun(
            self, train_score: float, test_score: float, max_gap: float = 0.1
    ):
        """
        Checks to make sure that the training and test scores are
        close to each other.
        """
        if abs(test_score - train_score) > max_gap:
            raise Exception(
                f"The training and test scores are too far apart! They are {train_score} and {test_score} respectively."
            )