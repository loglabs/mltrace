.. _quickstart:

Quickstart
==========

To use ``mltrace``, you first need to set up a server to log to. You will need the following utilities:

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

You can access the UI by navigating to ``<server_ip_address>:8080`` (or localhost:8080_ if you are running locally) in your browser. 

.. _mltrace: https://github.com/loglabs/mltrace/tree/v0.13
.. _localhost:8080: http://localhost:8080

Client
^^^^^^

To log to the server using the client library, install the latest version of mltrace on the machine executing your pipelines by running:
  
.. code-block:: python

    pip install mltrace

