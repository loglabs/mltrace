from datetime import datetime
from mltrace import Component, ComponentRun, log_component_run

import random
import string

training_component = Component(
    "training", "Example of training a model.", "data_scientist"
)
inference_component = Component(
    "inference", "Example of doing inference.", "ml_engineer"
)


@training_component.run(
    component_name="training",
    input_vars=["version"],
    output_vars=["model_file"],
)
def training(version: str) -> str:
    model_file = "model_" + version
    return model_file


@inference_component.run(
    component_name="inference",
    input_vars=["model_files"],
    output_vars=["identifier"],
)
def inference(model_files) -> str:
    identifier = "".join(
        random.choice(string.ascii_lowercase) for i in range(10)
    )
    return identifier


if __name__ == "__main__":
    # Run training once
    version = "0"
    first_model_file = training(version)

    # Fake a component run from 2 months ago
    now = datetime.utcnow()
    cr = ComponentRun(
        "some_old_component",
        start_timestamp=now.replace(month=now.month - 2),
        end_timestamp=now,
    )
    second_model_file = "model_1"
    cr.add_input("1")
    cr.add_output(second_model_file)
    log_component_run(cr)

    # Run training again
    version = "2"
    third_model_file = training(version)

    # Run inference on old model file. This should be stale!
    first_identifier = inference([first_model_file, second_model_file])
    print(first_identifier)
