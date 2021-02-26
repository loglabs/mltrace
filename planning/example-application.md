# Example Application

To test out and iterate and develop `mltrace`, we will have an example of an end-to-end pipeline that does some basic ML. It is hard to develop devtools in a vacuum :)

I really don't care about ML applications right now, so I will just pull something from thin air. Ideally, it is a toy but has enterprise-grade infrastructure (aws, Airflow, scheduled jobs, etc).

I will leverage the toy task I have trained models for before in [this notebook](https://github.com/shreyashankar/debugging-ml-talk/blob/main/nyc_taxi_2020.ipynb). For any record coming in, we want to predict whether the passenger will give a high tip or not. Our pipeline will consist of data transformations, models, and output transformations. 

For a first pass, I will build this system in a lightweight fashion to run on my machine. The raw data is stored in a public `s3` bucket. I will write the following components:

* data cleaning
* featurization
* preprocessing
* model inference
* [OPTIONAL] output postprocessing

I will train a model in an offline setting and use that for the model inference setting. For the first pass, I won't be dealing with versioning on the *model* -- just the data, if any. 

For the second pass, I will incorporate MLFlow models to do model versioning. I will think of some clever way to do data versioning (without using extra tools) -- if anything, it wil be another partition in a table.

