from flask import Flask, request, Response
from http import HTTPStatus
from mltrace.db import Store, PointerTypeEnum, ComponentRun as SQLComponentRun
from mltrace.entities import Component, ComponentRun, IOPointer

import json

app = Flask(__name__)
DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'


def error(err_msg, status_code):
    return Response(json.dumps({"error": err_msg}), status=status_code)


def serialize(trace: dict):
    """Serializes the result of web_trace."""
    if 'object' not in trace:
        return

    cr = trace['object']
    inputs = [IOPointer.from_dictionary(
        iop.__dict__).to_dictionary() for iop in cr.inputs]
    outputs = [IOPointer.from_dictionary(
        iop.__dict__).to_dictionary() for iop in cr.outputs]
    dependencies = [dep.component_name for dep in cr.dependencies]
    d = cr.__dict__
    if cr.code_snapshot:
        cr.code_snapshot = cr.code_snapshot.decode('utf-8')
    d.update({'inputs': inputs, 'outputs': outputs,
              'dependencies': dependencies})
    trace['object'] = str(ComponentRun.from_dictionary(d))

    # Recursively apply for child nodes
    if 'childNodes' in trace:
        for child_node in trace['childNodes']:
            serialize(child_node)


def serialize_component_run(cr: SQLComponentRun) -> str:
    """Serializes component run to display info on a card."""
    inputs = [IOPointer.from_dictionary(
        iop.__dict__).to_dictionary() for iop in cr.inputs]
    outputs = [IOPointer.from_dictionary(
        iop.__dict__).to_dictionary() for iop in cr.outputs]
    dependencies = [dep.component_name for dep in cr.dependencies]
    d = cr.__dict__
    if cr.code_snapshot:
        cr.code_snapshot = cr.code_snapshot.decode('utf-8')
    d.update({'inputs': inputs, 'outputs': outputs,
              'dependencies': dependencies})
    return str(ComponentRun.from_dictionary(d))


@app.route('/component_run', methods=['GET'])
def get_component_run():
    if 'id' not in request.args:
        return error(f'id not specified.', HTTPStatus.NOT_FOUND)

    component_run_id = request.args['id']
    store = Store(DB_URI)
    try:
        res = store.get_component_run(component_run_id)
        return json.dumps(serialize_component_run(res))
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
        cr = store.get_component_run(res['id'].replace('componentrun_', ''))
        serialize(res)
        return json.dumps(res)
    except RuntimeError:
        return error(f'Output {output_id} not found', HTTPStatus.NOT_FOUND)
