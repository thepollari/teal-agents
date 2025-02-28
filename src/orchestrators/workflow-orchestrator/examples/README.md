# Teal Agents - Workflow Orchestrator
## Examples
This directory includes several examples of workflows which can be run using the
Workflow Orchestrator.

### Prerequisites
The Workflow Orchestrator relies on [dapr](https://dapr.io/) as a workflow
engine and, as such, to run the examples locally, you will first need to start
dapr. To simplify this process, there is a docker compose file, in this
directory, which will start all required services.

```shell
docker compose up -d
```

### Running an Example
#### Set up Environment
To simplify running the examples, there is a helper script in this directory
called `orchestrator.py`. Before running, first sync the `uv` to install the
dependencies.
```shell
uv sync --prerelease=allow
```

#### Copy Environment File
To run an example, after starting dapr, copy that example's `example.env` file
in to this directory and rename it to `.env`.

#### Run the Example
Now, simply run the example by executing:
```shell
uv run --prerelease=allow -- python orchestrator.py
```