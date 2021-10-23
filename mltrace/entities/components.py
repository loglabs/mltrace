"""
This file defines different kinds of components and the 
corresponding tests for before and afterRun.
"""
from mltrace.entities.base_component import Component
from mltrace.entities.tests import OutliersTest

import typing


class PreprocessingComponent(Component):
    def __init__(
        self,
        owner: str,
        name: str = "Preprocessing",
        description: str = "Preprocessing features to feed into a model.",
        tags: typing.List[str] = [],
        beforeTests: list = [],
        afterTests: list = [],
    ):
        # default test for Preprocessing component
        afterTests = [OutliersTest]

        super().__init__(
            name=name,
            owner=owner,
            description=description,
            tags=tags,
            beforeTests=beforeTests,
            afterTests=afterTests,
        )
