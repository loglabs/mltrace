.. _quickstart:

Quickstart
==========

To use ``mltrace``, you first need to set up a server to log to. You will need the following utilities:

* Python 3.7 or later
* Docker_
* Postgres_
* Yarn_

.. _Docker: https://www.docker.com/products/docker-desktop
.. _Postgres: https://www.postgresql.org/download/
.. _Yarn: https://classic.yarnpkg.com/en/docs/install/


Server
^^^^^^

On the machine you would like to run the server (can be your local machine), clone the latest release of mltrace_. In the root directory, start the server by running:

.. code-block :: python

    docker-compose build
    docker-compose up [-d]

You can access the UI by navigating to ``<SERVER'S IP ADDRESS>:8080`` (or localhost:8080_ if you are running locally) in your browser. 

.. _mltrace: https://github.com/loglabs/mltrace
.. _localhost:8080: http://localhost:8080

Client
^^^^^^

To log to the server using the client library, install the latest version of mltrace on the machine executing your pipelines by running:
  
.. code-block:: python

    pip install mltrace

Next, you will need to set the database URI. It is recommended to use environment variables for this. To set the database address, set the ``DB_SERVER`` variable:

.. code-block :: python

    export DB_SERVER=<SERVER'S IP ADDRESS>

where ``<SERVER'S IP ADDRESS>`` is either the IP address of a remote machine or ``localhost`` if running locally. If, when you set up the server, you changed the URI in ``docker-compose.yaml``, you can set the ``DB_URI`` variable (which represents the entire database URI) client-side instead of ``DB_SERVER``.

