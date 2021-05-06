mltrace documentation
===================================

``mltrace`` is an open-source Python tool to track data flow through various
components in ML pipelines. It offers the following:

- coarse-grained lineage and tracing
- Python API to log versions of data and pipeline components
- database to store information about component runs
- UI to show the trace of steps in a pipeline taken to produce an output

``mltrace`` is designed specifically for Agile or multidisciplinary teams collaborating on machine learning or complex data pipelines.

Design principles
^^^^^^^^^^^^^^^^^

- Simplicity (users should know *exactly* what the tool does)
- Rinse and repeat other successful designs
    - Decorator design similar to Dagster solids_
    - Logging design similar to MLFlow tracking_
- API designed for both engineers and data scientists
- UI designed for people to help triage issues *even if they didn’t build the ETL or models themselves*

.. _solids: https://docs.dagster.io/concepts/solids-pipelines/solids
.. _tracking: https://www.mlflow.org/docs/latest/tracking.html


Guides
^^^^^^

.. toctree::
   :maxdepth: 2
   
   quickstart
   concepts
   logging
   querying
   All functions<mltrace>