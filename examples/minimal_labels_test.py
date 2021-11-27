from mltrace import Component

import random
import pandas as pd

from mltrace import delete_label, print_deleted_labels

first_component = Component("first", "shreya")
second_component = Component("second", "shreya")
third_component = Component("third", "shreya")


@first_component.run(input_vars={"df": "label"}, output_vars=["first_df"])
def first(df, label):
    first_df = df * 2
    return first_df


@second_component.run(auto_log=True)
def second(df):
    second_df = df * 2
    return second_df


@third_component.run(auto_log=True)
def third(df):
    third_df = df * 2
    return third_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {"test_col": [random.randint(0, 100) for _ in range(10)]}
    )
    df = first(df, "temp_label")
    delete_label("temp_label")
    third(second(df))
