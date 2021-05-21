.. _concepts:

Concepts
========

Machine learning pipelines, or even complex data pipelines, are made up of several *components.* For instance:

.. image:: images/toy-ml-pipeline-diagram.svg

Keeping track of data flow in and out of these components can be tedious, especially if multiple people are collaborating on the same end-to-end pipeline.This is because in ML pipelines, *different* artifacts are produced (inputs and outputs) when the *same* component is run more than once.

Knowing data flow is a precursor to debugging issues in data pipelines. ``mltrace`` also determines whether components of pipelines are stale.

Data model
^^^^^^^^^^

The two prominent client-facing abstractions are the :py:class:`~mltrace.entities.Component` and :py:class:`~mltrace.entities.ComponentRun` abstractions.

:py:class:`mltrace.entities.Component`
"""""""""

The ``Component`` abstraction represents a stage in a pipeline and its static metadata, such as:

* name
* description
* owner
* tags (optional list of string values to reference the component by)

Tags are generally useful when you have multiple components in a higher-level stage. For example, ETL computation could consist of different components such as "cleaning" or "feature generation." You could create the "cleaning" and "feature generation" components with the tag ``etl`` and then easily query component runs with the ``etl`` tag in the UI.

:py:class:`mltrace.entities.ComponentRun`
"""""""""

The ``ComponentRun`` abstraction represents an instance of a ``Component`` being run. Think of a ``ComponentRun`` instance as an object storing *dynamic* metadata for a ``Component``, such as:

* start timestamp
* end timestamp
* inputs
* outputs
* git hash
* source code
* dependencies (you do not need to manually declare)

If you dig into the codebase, you will find another abstraction, the :py:class:`~mltrace.entities.IOPointer`. Inputs and outputs to a ``ComponentRun`` are stored as ``IOPointer`` objects. You do not need to explicitly create an ``IOPointer`` -- the abstraction exists so that ``mltrace`` can easily find and store dependencies between ``ComponentRun`` objects.

You will not need to explicitly define all of these variables, nor do you have to create instances of a ``ComponentRun`` yourself. See the next section for logging functions and an example.

.. _Staleness Overview:

Staleness
^^^^^^^^^^

We define a component run as "stale" if it may need to be rerun. Currently, ``mltrace`` detects two types of staleness in component runs:

1. A significant number of days (default 30) have passed between when a component run's inputs were generated and the component is run
2. At the time a component is run, its dependencies have fresher runs that began before the component run started

We are working on "data drift" as another measure of staleness.
