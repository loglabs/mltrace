# mltrace

This tool tracks data flow through various components in ML pipelines and
contains a UI and API to show a trace of steps in an ML pipeline that produces
an output. It consists of an ORM-backed database, helper functions for users to
perform logging in their pipelines, and a UI for users to view metadata and
trace outputs.

The prototype is very lofi, but this `readme` contains instructions on how to
run the prototype on your machine.

![screenshot](./res/home.png)

## Quickstart

To get started, you will need to do 3 things:

1. Set up the database
2. Run some pipelines with logging
3. Launch the server and UI

### Database setup

We use Postgres-backed SQLAlchemy for now. Unfortunately the db uri is hardcoded
in multiple files, which I will change at some point. Assuming you have Docker
desktop, you can run  `docker-compose up -d` to set up the db.

If you don't want to use `docker-compose`, you can run the first Docker command off the bat to create the Postgres
instance:

```
# create a PostgreSQL instance
docker run --name postgres \
    -e POSTGRES_PASSWORD=admin \
    -e POSTGRES_USER=admin \
    -e POSTGRES_DB=sqlalchemy \
    -p 5432:5432 \
    -d postgres

# stop instance
docker stop postgres

# destroy instance
docker rm postgres
```

### Run pipelines

The files  `populate_db.py` and `populate_db_logging.py` include some fake
pipeline components with the relevant logging mechanisms. Pick one to run (I
suggest `populate_db.py`) and run it by executing `make run`. To execute
`populate_db_logging.py` you will need to run `make logrun`. Make will handle
the dependencies.

### Start webserver and launch UI

To start the Flask server, you can execute `make server`, which launches the
Flask app. To launch the UI, navigate to `./mltrace/server/ui` and execute `yarn
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