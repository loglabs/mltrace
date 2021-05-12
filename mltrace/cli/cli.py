# ------------------------- Imports ------------------------ #


import click
from mltrace.client import (
    # _db_uri,
    set_address,
    get_recent_run_ids,
    get_component_run_information,
    get_component_information,
)
import textwrap


# ------------------------- Utilities ------------------------ #


def set_server(url: str):
    set_address(url)


def show_info_card(run_id: int):
    cr_info = get_component_run_information(run_id)
    c_info = get_component_information(cr_info.component_name)

    click.echo(f"Name: {c_info.name}")
    click.echo(f"├─Owner: {c_info.owner}")
    click.echo(f"├─Desc: {c_info.description}")
    click.echo(f"├─Run ID: {run_id}")
    click.echo(f"├─Tags: {' '.join(c_info.tags)}")
    click.echo(f"├─Started: {cr_info.start_timestamp}")
    click.echo(f"├─Git: {cr_info.git_hash}")
    elapsed_time = cr_info.end_timestamp - cr_info.start_timestamp
    min, sec = divmod(elapsed_time.total_seconds(), 60)
    min = min + 1e-1 * sec
    click.echo(f"├─Duration: {min:0.3f} mins")
    click.echo("├─Inputs:")
    inputs = cr_info.inputs
    for idx, inp in enumerate(inputs):
        if idx == len(inputs) - 1:
            click.echo(f"│  └{inp['name']}")
        else:
            click.echo(f"│  ├─{inp['name']}")
    click.echo("├─Outputs:")
    outputs = cr_info.outputs
    for idx, out in enumerate(outputs):
        if idx == len(outputs) - 1:
            click.echo(f"│  └{out['name']}")
        else:
            click.echo(f"│  ├─{out['name']}")
    code = textwrap.indent(cr_info.code_snapshot, "│  ")
    click.echo(f"├─Code Snapshot:\n{code.rstrip()}")
    dependencies = (
        " ".join(cr_info.dependencies)
        if cr_info.dependencies
        else "None"
    )
    click.echo(f"└Dependencies: {dependencies}")
    click.echo()


# ------------------------- CLI ------------------------ #


@click.group()
def mltrace():
    pass


@mltrace.command("recent")
@click.option("--url", default="localhost", help="URL of the database.")
@click.option("--count", default=5, help="Count of recent objects.")
def recent(
    url: str,
    count: int,
):
    """
    CLI for recent objects.
    """
    # Set Server
    set_server(url)
    # Get the recent ids
    component_run_ids = get_recent_run_ids()
    for id in component_run_ids[:count]:
        show_info_card(id)
