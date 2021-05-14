from dateutil import parser
from flask import Blueprint, Flask, request, Response
from http import HTTPStatus
from mltrace.entities import Component, ComponentRun, IOPointer
from mltrace import (
    get_component_information,
    get_component_run_information,
    get_components_with_tag,
    get_history,
    web_trace,
    get_recent_run_ids,
    get_io_pointer,
    set_db_uri,
)

import copy
import json
import logging

app = Flask(__name__, static_folder="ui/build", static_url_path="")
api = Blueprint("api", __name__)


def error(err_msg, status_code):
    return Response(json.dumps({"error": err_msg}), status=status_code)


def serialize_component_run(c: Component, cr: ComponentRun) -> str:
    """Serializes component run to display info on a card."""
    web_cr_dict = json.loads(str(cr))

    # Add component information
    web_cr_dict["owner"] = c.owner
    web_cr_dict["description"] = c.description
    web_cr_dict["tags"] = c.tags

    return json.dumps(web_cr_dict)


@api.route("/component_run", methods=["GET"])
def component_run():
    if "id" not in request.args:
        return error(f"id not specified.", HTTPStatus.NOT_FOUND)

    component_run_id = request.args["id"]
    try:
        # Check to make sure the id is actually numeric
        if not component_run_id.isdigit():
            raise RuntimeError()
        component_run = get_component_run_information(component_run_id)
        component = get_component_information(component_run.component_name)
        return serialize_component_run(component, component_run)
    except RuntimeError:
        return error(
            f"Component run ID {component_run_id} not found", HTTPStatus.NOT_FOUND
        )


@api.route("/io_pointer", methods=["GET"])
def io_pointer():
    if "id" not in request.args:
        return error(f"id not specified.", HTTPStatus.NOT_FOUND)

    io_pointer_id = request.args["id"]
    try:
        res = get_io_pointer(io_pointer_id, create=False)
        return json.dumps(IOPointer.from_dictionary(res.__dict__).to_dictionary())
    except RuntimeError:
        return error(f"IOPointer {io_pointer_id} not found", HTTPStatus.NOT_FOUND)


@api.route("/tag", methods=["GET"])
def tag():
    if "id" not in request.args:
        return error(f"id not specified.", HTTPStatus.NOT_FOUND)

    tag_name = request.args["id"]
    try:
        components = get_components_with_tag(tag_name)
        return str(components)
    except RuntimeError:
        return error(f"Tag {tag_name} not found", HTTPStatus.NOT_FOUND)


@api.route("/history", methods=["GET"])
def history():
    if "component_name" not in request.args:
        return error(f"component_name not specified.", HTTPStatus.NOT_FOUND)

    component_name = request.args["component_name"]
    limit = request.args["limit"] if "limit" in request.args else None
    date_upper = (
        parser.parse(request.args["date_upper"])
        if "date_upper" in request.args
        else None
    )
    date_lower = (
        parser.parse(request.args["date_lower"])
        if "date_lower" in request.args
        else None
    )

    try:
        history = (
            get_history(component_name, limit, date_lower, date_upper)
            if limit
            else get_history(
                component_name, date_lower=date_lower, date_upper=date_upper
            )
        )
        return str(history)
    except RuntimeError:
        return error(f"Component {component_name} has no runs", HTTPStatus.NOT_FOUND)


@api.route("/component", methods=["GET"])
def component():
    if "id" not in request.args:
        return error(f"id not specified.", HTTPStatus.NOT_FOUND)

    component_name = request.args["id"]
    try:
        component = get_component_information(component_name)
        return str(component)
    except RuntimeError:
        return error(f"Component {component_name} not found", HTTPStatus.NOT_FOUND)


@api.route("/recent", methods=["GET"])
def recent():
    component_run_ids = (
        get_recent_run_ids(request.args["limit"])
        if "limit" in request.args
        else get_recent_run_ids()
    )
    return json.dumps(component_run_ids)


@api.route("/trace", methods=["GET"])
def trace():
    if "output_id" not in request.args:
        return error(f"output_id not specified.", HTTPStatus.NOT_FOUND)
    output_id = request.args["output_id"]
    try:
        res = web_trace(output_id)
        return json.dumps(res)
    except RuntimeError:
        return error(f"Output {output_id} not found", HTTPStatus.NOT_FOUND)


app.register_blueprint(api, url_prefix="/api")
