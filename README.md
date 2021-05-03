# mltrace

[![mltrace](https://github.com/loglabs/mltrace/actions/workflows/python-package.yml/badge.svg)](https://github.com/loglabs/mltrace/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/mltrace/badge/?version=latest)](https://mltrace.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/mltrace)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This tool tracks data flow through various components in ML pipelines and
contains a UI and API to show a trace of steps in an ML pipeline that produces
an output. It consists of an ORM-backed database, helper functions for users to
perform logging in their pipelines, and a UI for users to view metadata and
trace outputs.

The prototype is very lofi, but this `README` contains instructions on how to
run the prototype on your machine.

![screenshot](./res/home.png)

## Quickstart

You should have Docker installed on your machine. To get started, you will need to do 3 things:

1. Set up the database and Flask server
2. Run some pipelines with logging
3. Launch and UI

### Database and server setup

We use Postgres-backed SQLAlchemy. Unfortunately the db uri is hardcoded
in multiple files, which I will change at some point. 

Assuming you have Docker installed, you can run the following commands from the
root directory:

```
docker-compose build
docker-compose up
```

And then to tear down the containers, you can run `docker-compose down`.

### Run pipelines

The files  `populate_db.py` and `populate_db_logging.py` include some fake
pipeline components with the relevant logging mechanisms. Pick one to run (I
suggest `populate_db.py`) and run it by executing `make run`. To execute
`populate_db_logging.py` you will need to run `make logrun`. Make will handle
the dependencies.

### Launch UI

To launch the UI, navigate to `./mltrace/server/ui` and execute `yarn
install` then `yarn start`. The UI is based on `create-react-app`. Hopefully
navigating the UI is intuitive.

#### Commands supported in the UI

| Command | Description |
|---|---|
| `recent` | Shows recent component runs, also the home page|
| `history COMPONENT_NAME` | Shows history of runs for the component name. Defaults to 10 runs. Can specify number of runs by appending a positive integer to the command, like `history etl 15`|
| `inspect COMPONENT_RUN_ID` | Shows info for that component run ID |
| `trace OUTPUT_ID` | Shows a trace of steps for the output ID |
| `tag TAG_NAME` | Shows all components with the tag name|

## Code organization
