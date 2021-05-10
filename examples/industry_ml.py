"""
examples/industry_ml.py

This file contains several different components, mimicking that of a machine learning pipeline at a company:

- ingestion
- cleaning
- feature generation
- model training
- model inference

The code in each of these components is placeholder code. When you run this file, an output ID will be printed. You can then enter "trace {OUTPUT_ID}" in the UI's command bar to see the trace of steps that produced that output ID.
"""


from mltrace import (
    create_component,
    register,
    set_address,
    clean_db,
    get_components_with_tag,
)

import random
import string


@register(
    component_name="ingest",
    input_vars=["client_data_filename"],
    output_vars=["ingested_data_filename"],
)
def ingest(client_data_filename: str) -> str:
    # Ingest client's data into our data lake
    ingested_data_filename = f"ingested_{client_data_filename}"
    return ingested_data_filename


@register(
    component_name="clean", input_vars=["filename"], output_vars=["clean_data_filename"]
)
def clean(filename: str) -> str:
    # Read data into dataframe and clean it
    # df = pd.read_csv(filename)
    # clean the df
    clean_data_filename = f"clean_{filename}"
    return clean_data_filename


@register(
    component_name="featuregen",
    input_vars=["filename"],
    output_vars=["features_filename"],
)
def featuregen(filename: str) -> str:
    # Read data and make features
    # df = pd.read_csv(filename)
    # df[feature_columns] = ...
    features_filename = f"feature_{filename}"
    return features_filename


@register(
    component_name="training",
    input_vars=["filename", "dev_model"],
    output_vars=["model_filename"],
)
def training(filename: str, dev_model: str = "") -> str:
    # Read data and train model
    # df = pd.read_csv(filename)
    # model.train(df)
    model_filename = "model.joblib"
    if len(dev_model) > 0:
        model_filename = "prod_model.joblib"

    return model_filename


@register(
    component_name="inference",
    input_vars=["filename", "model_path"],
    output_vars=["output_id"],
)
def inference(filename: str, model_path: str) -> str:
    # Load model and data
    # Run some inference
    output_id = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    return output_id


if __name__ == "__main__":
    # Set server
    set_address("localhost")

    # Create components
    create_component(
        name="ingest",
        description="Example of ingesting data from some client.",
        owner="data_engineer",
        tags=["example"],
    )
    create_component(
        name="clean",
        description="Example of cleaning data.",
        owner="data_engineer",
        tags=["example"],
    )
    create_component(
        name="featuregen",
        description="Example of generating features.",
        owner="ml_engineer",
        tags=["example"],
    )
    create_component(
        name="training",
        description="Example of training a model.",
        owner="data_scientist",
        tags=["example"],
    )
    create_component(
        name="inference",
        description="Example of doing inference.",
        owner="ml_engineer",
        tags=["example"],
    )

    # Run with some fake client data
    historical_data_path = "historical_data.csv"
    live_data_path = "live_data.csv"

    # Train a model on historical data
    historical_ingested = ingest(historical_data_path)
    historical_clean = clean(historical_ingested)
    historical_features = featuregen(historical_clean)
    historical_model = training(historical_features)

    # Train production model
    production_model = training(historical_features, historical_model)

    # Do inference
    live_ingested = ingest(live_data_path)
    live_clean = clean(live_ingested)
    live_features = featuregen(live_clean)
    output_id = inference(live_features, production_model)

    print(f"Final output id: {output_id}")
