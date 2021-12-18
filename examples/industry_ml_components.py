"""

examples/industry_ml_components.py

This file contains the components required for running examples/industry_ml.py file.
We define the different components used during the pipeline in this file. 


"""
from mltrace.entities.base_component import Component

ingest_component = Component(name="ingest", description="Example of ingesting data from some client.", 
                            owner="data_engineer", tags=["example"])

clean_component = Component(name="clean", description="Example of cleaning data",
                            owner="data_engineer", tags=["example"])

featuregen_component = Component(name="featuregen", description="Example of generating features.",
                                owner="ml_engineer", tags=["example"])

training_component = Component(name="training", description="Example of training a model.",
                               owner="data_scientist", tags=["example"])

inference_component = Component(name="inference", description="Example of doing inference.",
                                owner="ml_engineer", tags=["example"]) 

