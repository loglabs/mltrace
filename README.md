# mltrace

[![mltrace](https://github.com/loglabs/mltrace/actions/workflows/python-package.yml/badge.svg)](https://github.com/loglabs/mltrace/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/mltrace/badge/?version=latest)](https://mltrace.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/mltrace)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`mltrace` tracks data flow through various components in ML pipelines and
contains a UI and API to show a trace of steps in an ML pipeline that produces
an output. It offers the following:

- coarse-grained lineage and tracing
- Python API to log versions of data and pipeline components
- database to store information about component runs
- UI to show the trace of steps in a pipeline taken to produce an output

`mltrace` is designed specifically for Agile or multidisciplinary teams collaborating on machine learning or complex data pipelines. The prototype is very lofi, but this `README` contains instructions on how to run the prototype on your machine **if you are interested in developing.** For general usage instructions, please see the [official documentation](https://mltrace.readthedocs.io/en/latest/).

![screenshot](./res/home.png)

## Quickstart

You should have Docker installed on your machine. To get started, you will need to do 3 things:

1. Set up the database and Flask server
2. Run some pipelines with logging
3. Launch the UI

If you are interested in learning about specific `mltrace` concepts, please read [this page](https://mltrace.readthedocs.io/en/latest/concepts.html) in the official docs.

### Database and server setup

We use Postgres-backed SQLAlchemy. Assuming you have Docker installed, you can run the following commands from the
root directory:

```
docker-compose build
docker-compose up [-d]
```

And then to tear down the containers, you can run `docker-compose down`.

### Run pipelines

To use the logging functions, you will need to install various dependencies:

```
pip install -r requirements.txt
pip install -e .
```

The files in the `examples` folder contain sample scripts you can run. For instance, if you run `examples/industry_ml.py`, you might get an output like:

```
> python examples/industry_ml.py
Final output id: zguzvnwsux
```

And if you trace this output in the UI (`trace zguzvnwsux`), you will get:

![screenshot](./res/industry_ml.png)


You can also look at `examples` for ways to integrate `mltrace` into your ML pipelines, or check out the [official documentation](https://mltrace.readthedocs.io/en/latest/).

### Launch UI

To launch the UI, navigate to `./mltrace/server/ui` and execute `yarn
install` then `yarn start`. The UI is based on `create-react-app`. Hopefully
navigating the UI is intuitive. It should be served at [localhost:3000](localhost:3000). Here's an example of what tracing an output would give:

![screenshot](./res/trace.png)

#### Commands supported in the UI

| Command | Description |
|---|---|
| `recent` | Shows recent component runs, also the home page|
| `history COMPONENT_NAME` | Shows history of runs for the component name. Defaults to 10 runs. Can specify number of runs by appending a positive integer to the command, like `history etl 15`|
| `inspect COMPONENT_RUN_ID` | Shows info for that component run ID |
| `trace OUTPUT_ID` | Shows a trace of steps for the output ID |
| `tag TAG_NAME` | Shows all components with the tag name|

### Future directions

The following projects are in the immediate roadmap:

* Displaying whether components are "stale" (i.e. you need to rerun a component such as training)
* REST API to log from any type of file, not just a Python file
* Prometheus integrations to monitor component output distributions
* Causal analysis for ML bugs — if you flag several outputs as mispredicted, which component runs were common in producing these outputs? Which component is most likely to be the biggest culprit in an issue?
* Support for finer-grained lineage (at the record level)

### Contributing

Anyone is welcome to contribute, and your contribution is greatly appreciated! Feel free to either create issues or pull requests to address issues.

1. Fork the repo
2. Create your branch (`git checkout -b YOUR_GITHUB_USERNAME/somefeature`)
3. Make changes and add files to the commit (`git add .`)
4. Commit your changes (`git commit -m 'Add something'`)
5. Push to your branch (`git push origin YOUR_GITHUB_USERNAME/somefeature`)
6. Make a pull request
