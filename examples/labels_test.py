"""
examples/labels_test.py

This file contains several different components, mimicking that
of a machine learning pipeline at a company:

- ingestion
- merging datasets
- model training
- model inference

The code in each of these components is placeholder code.
When you run this file, an output ID will be printed. You can
then enter "trace {OUTPUT_ID}" in the UI's command bar to see
the trace of steps that produced that output ID.
"""


from mltrace import Component

import random
import string

ingest_component = Component(
    "ingest",
    description="Example of ingesting data from some client.",
    owner="data_engineer",
    tags=["label"],
)

merge_component = Component(
    "merge",
    description="Example of merging data from multiple sources.",
    owner="data_engineer",
    tags=["label"],
)

train_component = Component(
    "train",
    description="Example of training a model.",
    owner="data_engineer",
    tags=["label"],
)

infer_component = Component(
    "infer",
    description="Example of inferring labels from a model.",
    owner="data_engineer",
    tags=["label"],
)


@ingest_component.run(
    input_filenames=["client_data_filename"],
    output_filenames=["ingested_data_filename"],
)
def ingest(client_data_filename: str, label_cols: list = []) -> str:
    # Ingest client's data into our data lake
    ingested_data_filename = f"ingested_{client_data_filename}"
    return ingested_data_filename


@merge_component.run(
    input_filenames=["client_data_filename1", "client_data_filename2"],
    output_filenames=["merged_data_filename"],
)
def merge(
    client_data_filename1: str,
    client_data_filename2: str,
    label_cols: list = [],
) -> str:
    # Merge two datasets
    merged_data_filename = f"ingested_{client_data_filename1}"
    return merged_data_filename


@train_component.run(
    input_filenames=["filename"],
    output_filenames=["model_filename"],
)
def training(filename: str, model_name: str = "") -> str:
    # Read data and train model
    # df = pd.read_csv(filename)
    # model.train(df)
    model_filename = "model.joblib"
    if len(model_filename) > 0:
        model_filename = f"{model_name}.joblib"

    return model_filename


@infer_component.run(
    input_filenames=["filename", "model_path"], output_filenames=["output_id"]
)
def inference(filename: str, model_path: str) -> str:
    # Load model and data
    # Run some inference
    output_id = "".join(
        random.choice(string.ascii_lowercase) for i in range(10)
    )
    return output_id


if __name__ == "__main__":
    # Run with some fake client data
    training_data_1 = "datafarm_emails.csv"
    training_data_2 = "infosearch_emails.csv"
    live_data_path = "mailserve_emails.csv"
    deleted_customers = []

    # Train a model on historical data
    train1_ingested = ingest(training_data_1)
    train2_ingested = ingest(training_data_2)

    # Train topic classification model
    merged_datasets = merge(train1_ingested, train2_ingested)
    classification_model = training(merged_datasets, "topic_classification")

    # Train spam filter
    spam_model = training(train2_ingested, "spam_filter")

    # Do inference
    live_ingested = ingest(live_data_path)
    print("Beginning topic classification of emails")
    topics_output_id = inference(live_ingested, classification_model)
    print(f"Final topics output id: {topics_output_id}")

    print("Beginning spam filtering of emails")
    spam_output_id = inference(live_ingested, spam_model)
    print(f"Final spam output id: {spam_output_id}")

    # Deletion request from one customer from training_data_1
    # print("Customer Alice requesting data deletion")
    # delete_customer(["Alice"])
    # deleted_customers.append("Alice")

    # # Run inference again and show it breaks--expect error?
    # live_ingested = ingest(live_data_path)
    # try:
    #     print("Beginning topic classification of emails")
    #     topics_output_id = inference(live_ingested, classification_model)
    #     print(f"Topics output id: {output_id}")
    # except LabelDeletedError as e:
    #     print(e)
    # try:
    #     print("Beginning spam filtering of emails")
    #     spam_output_id = inference(live_ingested, spam_model)
    #     print(f"Spam output id: {spam_output_id}")
    # except LabelDeletedError as e:
    #     print(e)

    # # Delete another customer
    # print("Customer Bob requesting data deletion")
    # delete_customer("Bob")
    # deleted_customers.append("Bob")

    # # Now 30 days later, refresh the datasets in order to retrain
    # # Automatic way to determine which models need to be re-run?
    # training_data_1_later = remove_labels(training_data_1, deleted_customers)
    # training_data_2_later = remove_labels(training_data_2, deleted_customers)

    # # Train topic classification model
    # merged_datasets = merge(training_data_1_later, training_data_2_later)
    # classification_model = training(merged_datasets, "topic_classification")

    # # Train spam filter
    # spam_model = training(training_data_2_later, "spam_filter")

    # # Do inference
    # live_ingested = ingest(live_data_path)
    # print("Beginning topic classification of emails")
    # topics_output_id = inference(live_ingested, classification_model)
    # print(f"Final topics output id: {topics_output_id}")

    # print("Beginning spam filtering of emails")
    # spam_output_id = inference(live_ingested, spam_model)
    # print(f"Final spam output id: {spam_output_id}")
