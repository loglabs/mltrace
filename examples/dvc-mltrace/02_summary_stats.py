import pandas as pd
from mltrace import create_component, register


@register(component_name="summary", input_vars=["input_filepath"],
          output_vars=['output_filepath'])
def summary(input_filepath: str, output_filepath: str) -> str:
    """
    print some simple stats about dataset
    """
    abalone_data = pd.read_csv(input_filepath)
    summary_stats = abalone_data.describe()
    summary_stats.to_csv(output_filepath, index=False)


if __name__ == "__main__":
    create_component(
      name="summary",
      description="print some simple stats about dataset",
      owner="jeanne",
      tags=['eda'],)
    summary('data/abalone.csv', 'data/summary_stats.csv')
