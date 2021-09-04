"""
examples/tiny.py

This file contains one component, a function to increment
a number, and runs that component 10 times. The output of
the ith component run is the input to the (i+1)th component
run. Thus if you trace the last output in the UI, you should
see that it depends on 9 things.
"""


from mltrace import create_component, register

import random
import string

_identifier = "".join(random.choice(string.ascii_lowercase) for i in range(10))


@register(
    component_name="tiny", input_vars=["inp_str"], output_vars=["out_str"]
)
def increment(inp: int) -> int:
    inp_str = f"{_identifier}_{str(inp)}"
    out_str = f"{_identifier}_{str(inp + 1)}"
    return inp + 1


if __name__ == "__main__":
    # Create component
    create_component(
        name="tiny",
        description="Example of a tiny component",
        owner="groot",
        tags=["example"],
    )

    # Run the tiny function with some fake inputs and outputs
    i = 0
    while i < 10:
        i = increment(i)
