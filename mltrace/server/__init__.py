from mltrace.client import flag_output_id, unflag_output_id
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
    add_notes_to_component_run,
    flag_output_id,
    unflag_output_id,
    review_flagged_outputs,
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
            f"Component run ID {component_run_id} not found",
            HTTPStatus.NOT_FOUND,
        )


@api.route("/io_pointer", methods=["GET"])
def io_pointer():
    if "id" not in request.args:
        return error(f"id not specified.", HTTPStatus.NOT_FOUND)

    io_pointer_id = request.args["id"]
    try:
        res = get_io_pointer(io_pointer_id, create=False)
        return json.dumps(
            IOPointer.from_dictionary(res.__dict__).to_dictionary()
        )
    except RuntimeError:
        return error(
            f"IOPointer {io_pointer_id} not found", HTTPStatus.NOT_FOUND
        )


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
        return error(
            f"Component {component_name} has no runs", HTTPStatus.NOT_FOUND
        )


@api.route("/component", methods=["GET"])
def component():
    if "id" not in request.args:
        return error(f"id not specified.", HTTPStatus.NOT_FOUND)

    component_name = request.args["id"]
    try:
        component = get_component_information(component_name)
        return str(component)
    except RuntimeError:
        return error(
            f"Component {component_name} not found", HTTPStatus.NOT_FOUND
        )


@api.route("/recent", methods=["GET"])
def recent():
    kwargs = request.args
    component_run_ids = get_recent_run_ids(**kwargs)
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


@api.route("/notes", methods=["GET", "POST"])
def add_notes():
    if "id" not in request.json:
        return error(f"ComponentRun id not specified.", HTTPStatus.NOT_FOUND)
    component_run_id = request.json["id"]
    notes = request.json["notes"]
    try:
        res = add_notes_to_component_run(component_run_id, notes)
        return json.dumps(res)
    except RuntimeError:
        return error(
            f"ComponentRun {component_run_id} unable to set notes to {notes}",
            HTTPStatus.NOT_FOUND,
        )


@api.route("/flag", methods=["POST"])
def flag():
    if "id" not in request.json:
        return error(f"IOPointer id not specified.", HTTPStatus.NOT_FOUND)
    iopointer_name = request.json["id"]
    try:
        res = flag_output_id(iopointer_name)
        return json.dumps(res)
    except RuntimeError:
        return error(
            f"ComponentRun {iopointer_name} unable to be flagged for review",
            HTTPStatus.NOT_FOUND,
        )


@api.route("/unflag", methods=["POST"])
def unflag():
    if "id" not in request.json:
        return error(f"IOPointer id not specified.", HTTPStatus.NOT_FOUND)
    iopointer_name = request.json["id"]
    try:
        res = unflag_output_id(iopointer_name)
        return json.dumps(res)
    except RuntimeError:
        return error(
            f"ComponentRun {iopointer_name} unable to be unflagged",
            HTTPStatus.NOT_FOUND,
        )


@api.route("/review", methods=["GET"])
def review():
    try:
        flagged_output_ids, trace_nodes_counts = review_flagged_outputs()
        cr_ids_counts = [
            (node.id, count) for node, count in trace_nodes_counts
        ]
        return json.dumps([flagged_output_ids, cr_ids_counts])
    except RuntimeError:
        return error(
            "Flagged outputs unable to be reviewed",
            HTTPStatus.NOT_FOUND,
        )


app.register_blueprint(api, url_prefix="/api")
