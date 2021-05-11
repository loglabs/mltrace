import click
from mltrace.client import (
    _db_uri,
    set_address,
    get_recent_run_ids,
)

# Set server
set_address("localhost")

@click.group()
def mltrace():
    pass

@mltrace.command()
def recent():
    component_run_ids = get_recent_run_ids()
    click.echo(component_run_ids)

