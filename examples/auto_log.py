"""
examples/auto_log.py
This file contains one component and four different
functions that are used to demonstrate the auto_log
functionality. The user does not need to manually
define inputs and outputs.
"""

from mltrace import Component
from mltrace.entities import *

import mltrace
import pandas as pd
import random

c = Component(
    name="test_auto_logging",
    description="Tests implementation of automatically logging I/O.",
    owner="me",
)


@c.run(auto_log=True)
def create_data(arr):
    df = pd.DataFrame(arr)
    return df


@c.run(auto_log=True)
def double_data(df):
    new_df = df * 2
    return new_df


@c.run(auto_log=True)
def triple_data(df):
    new_df = df * 3
    return new_df


@c.run(auto_log=True)
def quadruple_data(df):
    new_df = df * 4
    mltrace.save(new_df)
    return new_df


if __name__ == "__main__":
    # Create a component.
    print("Generating array...")
    arr = [random.randint(0, 100) for _ in range(int(1e7))]
    print("Array generated.")
    df = create_data(arr)
    df = double_data(df)
    df = triple_data(df)
    df = quadruple_data(df)
    print(df)
