import pandas as pd
from mltrace import Component


c = Component(
    name="summary",
    description="print some simple stats about dataset",
    owner="jeanne",
    tags=["eda"],
)


@c.run(input_vars=["input_filepath"], output_filenames=["output_filepath"])
def summary(input_filepath: str, output_filepath: str) -> str:
    """
    print some simple stats about dataset
    """
    abalone_data = pd.read_csv(input_filepath)
    summary_stats = abalone_data.describe()
    summary_stats.to_csv(output_filepath, index=False)


if __name__ == "__main__":
    summary("data/abalone.csv", "data/summary_stats.csv")
