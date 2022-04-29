from mltrace.db import Store
from mltrace.db.utils import _load
from mltrace.entities import IOPointer, ComponentRun

import copy
import logging
import os
import typing


def _set_address_helper(old_uri: str, address: str):
    first = old_uri.split("@")[0]
    last = old_uri.split("@")[1].split(":")[1]
    return first + "@" + address + ":" + last


_db_uri = os.environ.get("DB_URI")
if _db_uri is None:
    _db_uri = "postgresql://admin:admin@localhost:5432/sqlalchemy"
    if os.environ.get("DB_SERVER"):
        _db_uri = _set_address_helper(_db_uri, os.environ.get("DB_SERVER"))
    else:
        logging.warning(
            f"Please set DB_URI or DB_SERVER as an environment variable. \
            Otherwise, DB_URI is set to {_db_uri}."
        )


# --------------------- Database management functions ------------------- #


def set_db_uri(uri: str):
    global _db_uri
    _db_uri = uri


def get_db_uri() -> str:
    global _db_uri
    return _db_uri


def set_address(address: str):
    global _db_uri
    _db_uri = _set_address_helper(_db_uri, address)

# helper function - convert to client facing component runs


def convertToClient(componentRuns: typing.List):
    component_runs = []
    for cr in componentRuns:

        inputs = []
        for iop in cr.inputs:
            iop_dict = IOPointer.from_dictionary(iop.__dict__).to_dictionary()
            iop_dict['value'] = _load(iop_dict['name'])
            inputs.append(iop_dict)

        outputs = []
        for iop in cr.outputs:
            iop_dict = IOPointer.from_dictionary(iop.__dict__).to_dictionary()
            iop_dict['value'] = _load(iop_dict['name'])
            outputs.append(iop_dict)

        dependencies = [dep.component_name for dep in cr.dependencies]
        d = copy.deepcopy(cr.__dict__)
        d.update(
            {
                "inputs": inputs,
                "outputs": outputs,
                "dependencies": dependencies,
            }
        )
        component_runs.append(ComponentRun.from_dictionary(d))
    return component_runs
