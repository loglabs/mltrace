"""
examples/newFrameworkTest.py

This file contains one component, a function to increment
a number, and runs that component 10 times. The output of
the ith component run is the input to the (i+1)th component
run. Thus if you trace the last output in the UI, you should
see that it depends on 9 things.
"""

from mltrace.entities import components

import pandas as pd
import numpy as np
import random
import string

_identifier = "".join(random.choice(string.ascii_lowercase) for i in range(10))

c = components.PreprocessingComponent(
    owner="aditi", description="tests output for outliers"
)


@c.run(input_vars=["type", "n"], output_vars=["testOutput"])
def gen_fake_data(
    type: str,
    n: int = 1000,
):
    df = pd.DataFrame(
        np.random.normal(1.0, 1.0, n)
        if type == "normal"
        else np.random.wald(1.0, 1.0, n),
        columns=["rando"],
    )
    testOutput = "hello world!"
    print(testOutput)
    return testOutput


if __name__ == "__main__":
    # Run the tiny function with some fake inputs and outputs
    gen_fake_data("wald")
