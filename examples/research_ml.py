"""
examples/research_ml.py

This file contains one large component. Although mltrace is
primarily designed for more collaborative ML pipelines (where
more than one person is actively developing code for the prediction
task), here's an example of using mltrace to keep track of some of
the experiments you might have run.

If you navigate to the UI and run `history research_model_development`,
you will see a list of runs for the `research_model_development`
component and their logged inputs/outputs.

However, using something like wandb or mlflow might be better for
research. This is because mltrace inputs and outputs are not stored
as key/value pairs; only the values are stored.
"""

from mltrace import Component

import itertools
import random


c = Component(
    name="research_model_development",
    description="Example of training a model for research.",
    owner="neurips_queen",
    tags=["example"],
)


@c.run(
    input_vars=["lr", "num_epochs", "hidden_size"],
    output_vars=["model_metric"],
)
def train_and_evaluate_model(lr, num_epochs, hidden_size):
    # Grab some random accuracy
    model_metric = f"{random.uniform(0, 1)}_accuracy"
    return model_metric


if __name__ == "__main__":

    lr_candidates = [0.001, 0.01, 0.1]
    num_epochs_candidates = [10, 50, 100]
    hidden_size_candidates = [64, 128, 256]

    candidates = itertools.product(
        lr_candidates, num_epochs_candidates, hidden_size_candidates
    )

    for lr, num_epochs, hidden_size in candidates:
        train_and_evaluate_model(
            f"lr_{lr}",
            f"num_epochs_{num_epochs}",
            f"hidden_size_{hidden_size}",
        )
