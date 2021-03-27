from flask import Flask, request, Response
from http import HTTPStatus
from mltrace.db import Store

import json

app = Flask(__name__)
DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'


def error(err_msg, status_code):
    return Response(json.dumps({"error": err_msg}), status=status_code)


@app.route('/trace', methods=['GET'])
def trace():
    if 'output_id' not in request.args:
        return error(f'output_id not specified.', HTTPStatus.NOT_FOUND)
    output_id = request.args['output_id']
    store = Store(DB_URI)
    try:
        res = json.dumps(store.web_trace(output_id))
        return res
    except RuntimeError:
        return error(f'Output {output_id} not found', HTTPStatus.NOT_FOUND)
