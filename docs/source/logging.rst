.. _logging:

Logging
========

``mltrace`` functions can be added to existing Python files to log component and run information to the server. Logging can be done via a decorator or explicit Python API. All logging functions are defined in the :py:mod:`mltrace` module, which you can install via pip:

.. code-block :: python

    pip install mltrace

For this example, we will add logging functions to a hypothetical ``cleaning.py`` that loads raw data and cleans it. In your Python file, before you call any logging functions, you will need to make sure you are connected to your server. You can easily do so by setting the environment variable ``DB_SERVER`` to your server's IP address:

.. code-block :: python

    export DB_SERVER=SERVER_IP_ADDRESS

where ``SERVER_IP_ADDRESS`` is your server's IP address or "localhost" if you are running locally. You can also call ``mltrace.set_address(SERVER_IP_ADDRESS)`` in your Python script instead if you do not want to set the environment variable.

If you plan to use the auto logging functionalities for component run inputs and outputs (turned off by default), you will need to set the environment variable ``SAVE_DIR`` to the directory you want to save versions of your inputs and outputs to. The default is ``.mltrace`` in the user directory.

Component creation
^^^^^^^^^^^^^^^^^^

For runs of components to be logged, you must first create the components themselves using :py:class:`mltrace.Component`. You can subclass the main Component class if you want to make a custom Component, for example:

.. code-block :: python

    from mltrace import Component

    class Cleaning(Component):
        def __init__(self, name, owner, tags=[], beforeTests=[], afterTests=[]):

            super().__init__(
                name="cleaning_" + name,
                owner=owner,
                description="Basic component to clean raw data",
                tags=tags,
                beforeTests=beforeTests,
                afterTests=afterTests,
            )

Components are intended to be defined once and reused throughout your application. You can define them in a separate file or folder and import them into your main Python application. If you do not want a custom component, you can also just use the default Component class, as shown below.

Logging runs
^^^^^^^^^^^^

Decorator approach
"""""""""

Suppose we have a function ``clean`` in our ``cleaning.py`` file:

.. code-block :: python

    import pandas as pd

    def clean_data(df: pd.DataFrame) -> str:
        # Do some cleaning
        clean_df = ...
        return clean_df

We can include the :py:func:`~mltrace.Component.run` decorator such that every time this function is run, dynamic information is logged:

.. code-block :: python

    from mltrace import Component
    import pandas as pd

    c = Component(
        name="cleaning",
        owner="plumber",
        description="Cleans raw NYC taxicab data",
    )

    @c.run(auto_log=True)
    def clean_data(df: pd.DataFrame) -> str:
        # Do some cleaning
        clean_df = ...
        return clean_df

We will refer to ``clean_data`` as the clean_data as the decorated component run function. The ``auto_log`` parameter is set to False by default, but you can set it to True to automatically log inputs and outputs. If ``auto_log`` is True, ``mltrace`` will save and log paths to any dataframes, variables with "data" or "model" in their names, and any other variables greater than 1MB. ``mltrace`` will save to the directory defined by the environment variable ``SAVE_DIR``. If ``MLTRACE_DIR`` is not set, ``mltrace`` will save to a ``.mltrace`` folder in the user directory.

If you do not set ``auto_log`` to True, then you will need to manually define your input and output variables in the :py:func:`~mltrace.Component.run` function. Note that ``input_vars`` and ``output_vars`` correspond to variables in the function. Their values at the time of return are logged. The start and end times, git hash, and source code snapshots are automatically captured. The dependencies are also automatically captured based on the values of the input variables.

Python approach
"""""""""

You can also create an instance of a :py:class:`~mltrace.ComponentRun` and log it using :py:func:`mltrace.log_component_run` yourself for greater flexibility. An example of this is as follows:

.. code-block :: python

    from datetime import datetime
    from mltrace import ComponentRun
    from mltrace import get_git_hash, log_component_run
    import pandas as pd

    def clean_data(filename: str) -> str:
        # Create ComponentRun object
        cr = ComponentRun("cleaning")
        cr.set_start_timestamp()
        cr.add_input(filename)
        cr.git_hash = get_git_hash() # Sets git hash, not source code snapshot!

        df = pd.read_csv(filename)
        # Do some cleaning
        ...
        # Save cleaned dataframe
        clean_version = filename[:-4] + '_clean_{datetime.utcnow().strftime("%m%d%Y%H%M%S")}.csv'
        df.to_csv(clean_version)

        # Finish logging
        cr.set_end_timestamp()
        cr.add_output(clean_version)
        log_component_run(cr)

        return clean_version

Note that in :py:func:`~mltrace.log_component_run`, ``set_dependencies_from_inputs`` is set to ``True`` by default. You can set it to False if you want to manually specify the names of the components that this component run depends on. To manually specify a dependency, you can call :py:func:`~mltrace.ComponentRun.set_upstream` with the dependent component name or list of component names before you call :py:func:`~mltrace.log_component_run`.

Testing
^^^^^^^

You can define Tests, or reusable blocks of computation, to run before and after components are run. To define a test, you need to subclass the :py:class:`~mltrace.Test` class. Defining a test is similar to defining a Python unittest, for example:

.. code-block :: python

    from mltrace import Test

    class OutliersTest(Test):
        def __init__(self):
            super().__init__(name='outliers')

        def testComputeStats(self; df: pd.DataFrame):
            # Get numerical columns
            num_df = df.select_dtypes(include=["number"])

            # Compute stats
            stats = num_df.describe()
            print("Dataframe statistics:")
            print(stats)
        
        def testZScore(
            self,
            df: pd.DataFrame,
            stdev_cutoff: float = 5.0,
            threshold: float = 0.05,
        ):
            """
            Checks to make sure there are no outliers using z score cutoff.
            """
            # Get numerical columns
            num_df = df.select_dtypes(include=["number"])

            z_scores = (
                (num_df - num_df.mean(axis=0, skipna=True))
                / num_df.std(axis=0, skipna=True)
            ).abs()

            if (z_scores > stdev_cutoff).to_numpy().sum() > threshold * len(df):
                print(
                    f"Number of outliers: {(z_scores > stdev_cutoff).to_numpy().sum()}"
                )
                print(f"Outlier threshold: {threshold * len(df)}")
                raise Exception("There are outlier values!")


Any function you expect to execute as a test must be prefixed with the name ``test`` in lowercase, like ``testSomething``. Arguments to test functions must be defined in the decorated component run function signature if the tests will be run before the component run function; otherwise the arguments to test functions must be defined as variables somewhere in the decorated component run function. You can integrate the tests into components in the constructor:

.. code-block :: python

    from mltrace import Component
    import pandas as pd

    c = Component(
        name="cleaning",
        owner="plumber",
        description="Cleans raw NYC taxicab data",
        beforeTests=[OutliersTest],
    )

    @c.run(auto_log=True)
    def clean_data(df: pd.DataFrame) -> str:
        # Do some cleaning
        clean_df = ...
        return clean_df

At runtime, the ``OutliersTest`` test functions will run before the ``clean_data`` function. Note that all arguments to the test functions executed in ``beforeTests`` must be arguments to ``clean_data``. All arguments to the test functions executed in ``afterTests`` must be variables defined somewhere in ``clean_data``.

End-to-end example
^^^^^^^^^^^^^^^^^^

To see an example of ``mltrace`` integrated into a Python pipeline, check out this `tutorial <https://github.com/loglabs/mltrace-demo>`_. The full pipeline with ``mltrace`` integrations is defined in ``solutions/main.py``. 