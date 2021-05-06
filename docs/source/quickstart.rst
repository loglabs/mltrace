.. _quickstart:

Quickstart
==========

To use `mltrace`, you first need to set up a server to log to. You will need the following utilities:

* [Docker](https://www.docker.com/products/docker-desktop)
* [Postgres](https://www.postgresql.org/download/)
* [Yarn]


## Server

On the machine you would like to run the server (can be your local machine), clone the latest version of [`mltrace`](https://github.com/loglabs/mltrace.git) and start the server by running:

.. code-block :: python

    docker-compose up [-d]

To set up the UI, navigate to `mltrace/server/ui` and run:

.. code-block :: python

    yarn install
    yarn start

Then you can navigate to `<server_ip_address>:3000` to use the UI.

## Client

To log to the server using the client library, install the latest version of mltrace on the machine executing your pipelines by running:
  
.. code-block:: python

    pip install mltrace

