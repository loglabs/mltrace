from flask import Flask, request, Response
from http import HTTPStatus
from mltrace.db import Store, PointerTypeEnum, Component as SQLComponent, ComponentRun as SQLComponentRun
from mltrace.entities import Component, ComponentRun, IOPointer
from mltrace import get_component_information, get_component_run_information

import copy
import json

app = Flask(__name__)
DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'


def error(err_msg, status_code):
    return Response(json.dumps({"error": err_msg}), status=status_code)


def serialize_component_run(c: Component, cr: ComponentRun) -> str:
    """Serializes component run to display info on a card."""
    web_cr_dict = json.loads(str(cr))

    # Add component information
    web_cr_dict['owner'] = c.owner
    web_cr_dict['description'] = c.description
    web_cr_dict['tags'] = c.tags

    return json.dumps(web_cr_dict)


@app.route('/component_run', methods=['GET'])
def get_component_run():
    if 'id' not in request.args:
        return error(f'id not specified.', HTTPStatus.NOT_FOUND)

    component_run_id = request.args['id']
    try:
        component_run = get_component_run_information(component_run_id)
        component = get_component_information(component_run.component_name)
        return serialize_component_run(component, component_run)
    except RuntimeError:
        return error(f'Component run ID {component_run_id} not found', HTTPStatus.NOT_FOUND)


@app.route('/io_pointer', methods=['GET'])
def get_io_pointer():
    if 'id' not in request.args:
        return error(f'id not specified.', HTTPStatus.NOT_FOUND)

    io_pointer_id = request.args['id']
    store = Store(DB_URI)
    try:
        res = store.get_io_pointer(io_pointer_id, create=False)
        return json.dumps(IOPointer.from_dictionary(res.__dict__).to_dictionary())
    except RuntimeError:
        return error(f'IOPointer {io_pointer_id} not found', HTTPStatus.NOT_FOUND)


@app.route('/trace', methods=['GET'])
def trace():
    if 'output_id' not in request.args:
        return error(f'output_id not specified.', HTTPStatus.NOT_FOUND)
    output_id = request.args['output_id']
    store = Store(DB_URI)
    try:
        res = store.web_trace(output_id)
        return json.dumps(res)
    except RuntimeError:
        return error(f'Output {output_id} not found', HTTPStatus.NOT_FOUND)
