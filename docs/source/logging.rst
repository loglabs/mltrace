.. _logging:

Logging
========

``mltrace`` functions can be added to existing Python files to log component and run information to the server. Logging can be done via a decorator or explicit Python API. All logging functions are defined in the :py:mod:`mltrace` module, which you can install via pip:

.. code-block :: python

    pip install mltrace

For this example, we will add logging functions to a hypothetical ``cleaning.py`` that loads raw data and cleans it. In your Python file, before you call any logging functions, you will need to make sure you are connected to your server. To do so, include the following code snippet at the beginning of your file:

.. code-block :: python

    import mltrace
    mltrace.set_address(SERVER_IP_ADDRESS)

where ``SERVER_IP_ADDRESS`` is your server's IP address or "localhost" if you are running locally.

Component creation
^^^^^^^^^^^^^^^^^^

For runs of components to be logged, you must first create the components themselves using :py:func:`mltrace.create_component`. For example:

.. code-block :: python

    mltrace.create_component(
        name="cleaning",
        description="Removes records with data out of bounds",
        owner="shreya",
        tags=["etl"],
    )

You only need to do this once; however nothing happens if you run this code snippet more than once. It is fine to leave it in your Python file to run every time this file is run. If the component hasn't been created, you cannot have any runs of this component name. This is to enforce users to enter static metadata about a component, such as the description and owner, to better facilitate collaboration.

Logging runs
^^^^^^^^^^^^

Decorator approach
"""""""""

Suppose we have a function ``clean`` in our ``cleaning.py`` file:

.. code-block :: python

    from datetime import datetime
    import pandas as pd

    def clean_data(filename: str) -> str:
        df = pd.read_csv(filename)
        # Do some cleaning
        ...
        # Save cleaned dataframe
        clean_version = filename + '_clean_{datetime.utcnow().strftime("%m%d%Y%H%M%S")}.csv'
        df.to_csv(clean_version)
        return clean_version

We can include the :py:func:`~mltrace.register` decorator such that every time this function is run, dynamic information is logged:

.. code-block :: python

    from datetime import datetime
    from mltrace import register
    import pandas as pd

    @register(
        component_name="cleaning", input_vars=["filename"], output_vars=["clean_version"]
    )
    def clean_data(filename: str) -> str:
        df = pd.read_csv(filename)
        # Do some cleaning
        ...
        # Save cleaned dataframe
        clean_version = filename + '_clean_{datetime.utcnow().strftime("%m%d%Y%H%M%S")}.csv'
        df.to_csv(clean_version)
        return clean_version

Note that ``input_vars`` and ``output_vars`` correspond to variables in the function. Their values at the time of return are logged. The start and end times, git hash, and source code snapshots are automatically captured. The dependencies are also automatically captured based on the values of the input variables.

Python approach
"""""""""

You can also create an instance of a :py:class:`~mltrace.entities.ComponentRun` and log it using :py:func:`mltrace.log_component_run` yourself for greater flexibility. An example of this is as follows:

.. code-block :: python

    from datetime import datetime
    from mltrace.entities import ComponentRun
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

Note that in :py:func:`~mltrace.log_component_run`, ``set_dependencies_from_inputs`` is set to ``True`` by default. You can set it to False if you want to manually specify the names of the components that this component run depends on. To manually specify a dependency, you can call :py:func:`~mltrace.entities.ComponentRun.set_upstream` with the dependent component name or list of component names before you call :py:func:`~mltrace.log_component_run`.

End-to-end example
^^^^^^^^^^^^^^^^^^

To put it all together, here's an end to end example of ``cleaning.py``:

.. code-block :: python

    """
    cleaning.py

    File that cleans data.
    """

    from datetime import datetime
    from mltrace import create_component, register, set_address
    import pandas as pd

    @register(
        component_name="cleaning", input_vars=["filename"], output_vars=["clean_version"]
    )
    def clean_data(filename: str) -> str:
        df = pd.read_csv(filename)
        # Do some cleaning
        ...
        # Save cleaned dataframe
        clean_version = filename + '_clean_{datetime.utcnow().strftime("%m%d%Y%H%M%S")}.csv'
        df.to_csv(clean_version)
        return clean_version
    
    if __name__ == "__main__"::
        # Set hostname and create component
        set_address("localhost")
        create_component(
            name="cleaning",
            description="Removes records with data out of bounds",
            owner="shreya",
            tags=["etl"],
        )

        # Run cleaning function
        clean_data("raw_data.csv")

That's it! Now, every time this file is run, a new run for the cleaning component is logged. The next step will demonstrate how to query and use the UI.
