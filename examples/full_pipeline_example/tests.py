"""
This file specifies different kinds of tests and the
functions to be run within each test.
"""
from mltrace.entities.base_test import Test
from mltrace.entities import utils

import pandas as pd


class OutliersTest(Test):
    def __init__(self):
        super().__init__("Outliers")

    def testZscore(self, df: pd.DataFrame, stdev_cutoff: float = 5.0):
        """
        Checks to make sure there are no outliers using z score cutoff.
        """
        z_scores = (
                (df - df.mean(axis=0, skipna=True)) /
                df.std(axis=0, skipna=True)
        ).abs()

        self.assertGreater(0, (z_scores > stdev_cutoff).to_numpy().sum(),
                           "There are outlier values!")

    # log result of test and stdout
