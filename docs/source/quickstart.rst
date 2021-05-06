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

On the machine you would like to run the server (can be your local machine), clone the latest version of mltrace_. In the root directory, start the server by running:

.. code-block :: python

    docker-compose up [-d]

To set up the UI, navigate to ``mltrace/server/ui`` and run:

.. code-block :: python

    yarn install
    yarn start

Then you can navigate to ``<server_ip_address>:3000`` (or localhost:3000_ if you are running locally) to use the UI.

.. _mltrace: https://github.com/loglabs/mltrace
.. _localhost:3000: http://localhost:3000

Client
^^^^^^

To log to the server using the client library, install the latest version of mltrace on the machine executing your pipelines by running:
  
.. code-block:: python

    pip install mltrace

