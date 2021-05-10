.. _querying:

Querying
========

The simplest way to query the logged runs is to use the ``mltrace`` UI. There are also some functions defined in the :py:mod:`mltrace` module for querying.

Using the UI
^^^^^^^^^^^^

As mentioned in the :ref:`quickstart`, you should set up the database, server, and UI using ``docker-compose``. The UI starts up showing the results of the ``recent`` command, or the most recent component runs logged.

.. image:: images/darkrecent.png

You can toggle between light and dark mode using the moon or sun button at the top right. You can also view a list of supported commands by clicking the help or question mark button at the top right. The commands currently supported are below:

+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------+
| Command     | Description                                                                                                                                                                                   | Usage                         |
+=============+===============================================================================================================================================================================================+===============================+
| ``recent``  | Displays the most recent runs across all components. Also serves as the default or "home" page.                                                                                               | ``recent``                    |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------+
| ``history`` | Displays most recent runs for a given component name. Shows latest 10 runs by default, but you can specify the number of runs you want to see by appending a positive integer to the command. | ``history COMPONENT_NAME 15`` |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------+
| ``inspect`` | Displays information such as inputs/outputs, code, git snapshot, owner, and more for a given component run ID.                                                                                | ``inspect COMPONENT_RUN_ID``  |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------+
| ``trace``   | Displays a trace of versioned steps that produced a given output.                                                                                                                             | ``trace OUTPUT_NAME``         |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------+
| ``tag``     | Displays all components with the given tag name.                                                                                                                                              | ``tag TAG_NAME``              |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------+


:py:mod:`mltrace` module functions
^^^^^^^^^^^^^^^^^^

- :py:func:`~mltrace.backtrace`
- :py:func:`~mltrace.get_component_information`
- :py:func:`~mltrace.get_component_run_information`
- :py:func:`~mltrace.get_components_with_owner`
- :py:func:`~mltrace.get_components_with_tag`
- :py:func:`~mltrace.get_history`
- :py:func:`~mltrace.get_recent_run_ids`