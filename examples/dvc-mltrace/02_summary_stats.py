import pandas as pd
from mltrace import create_component, register


@register(component_name="summary", input_vars=["input_filepath"])
def summary(input_filepath: str) -> str:
    """
    print some simple stats about dataset
    """
    a = pd.read_csv(input_filepath)
    print('counting null values')
    print(a.isna().sum())
    print('counting number of rows')
    print(a.shape[0])
    print('counting number of columns')
    print(a.shape[1])


if __name__ == "__main__":
    create_component(
      name="summary",
      description="print some simple stats about dataset",
      owner="jeanne",
      tags=['eda'],)
    summary('data/abalone.csv')
