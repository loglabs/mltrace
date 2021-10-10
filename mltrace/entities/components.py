"""
This file defines different kinds of components and the corresponding tests for before and afterRun.
"""
from mltrace.entities.base_component import Component
from mltrace.entities.tests import Outliers

class PreprocessingComponent(Component):

    def __init__(
            self,
            owner: str,
            beforeTests: list = [],
            afterTests: list = []
    ):
        # default test for Preprocessing component
        afterTests = afterTests.append(Outliers)

        super().__init__("PreprocessingComponents", owner, beforeTests, afterTests)
