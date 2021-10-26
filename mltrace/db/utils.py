from mltrace.db.base import Base
from mltrace.db.models import ComponentRun, PointerTypeEnum
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.schema import (
    DropConstraint,
    DropTable,
    MetaData,
    Table,
    ForeignKeyConstraint,
)

import hashlib
import inspect
import joblib
import os
import pandas as pd
import random
import sqlalchemy
import string
import time
import typing


def _create_engine_wrapper(
    uri: str, max_retries=5
) -> sqlalchemy.engine.base.Engine:
    """Creates engine using sqlalchemy API. Includes max retries parameter."""
    retries = 0
    while retries < max_retries:
        try:
            engine = create_engine(uri)
            return engine
        except Exception as e:
            print(f"DB could not be created with exception {e}. Trying again.")
        retries += 1
    raise RuntimeError("Max retries hit.")


def _initialize_db_tables(engine: sqlalchemy.engine.base.Engine):
    """Initializes tables using sqlalchemy API."""
    Base.metadata.create_all(engine)


def _drop_everything(engine: sqlalchemy.engine.base.Engine):
    """(On a live db) drops all foreign key constraints before dropping all
    tables. Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """

    con = engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for
    # postgres (based on the actual schema of the running instance)
    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()
    Base.metadata.drop_all(engine)


def _map_extension_to_enum(filename: str) -> PointerTypeEnum:
    """Infers the relevant enum for the filename."""
    data_extensions = [
        "csv",
        "pq",
        "parquet",
        "txt",
        "md",
        "rtf",
        "tsv",
        "xml",
        "pdf",
        "mlt",
    ]
    model_extensions = [
        "h5",
        "hdf5",
        "joblib",
        "pkl",
        "pickle",
        "ckpt",
        "mlmodel",
    ]

    words = filename.split(".")

    if len(words) < 1:
        return PointerTypeEnum.UNKNOWN

    extension = words[-1].lower()

    if extension in data_extensions:
        return PointerTypeEnum.DATA

    if extension in model_extensions:
        return PointerTypeEnum.MODEL

    # TODO(shreyashankar): figure out how to handle output id
    return PointerTypeEnum.UNKNOWN


def _hash_value(value: typing.Any = "") -> bytes:
    """Hashes a value using the sqlalchemy API."""
    if isinstance(value, str) and value == "":
        return b""
    return hashlib.sha256(repr(value).encode()).digest()


# TODO(shreyashankar): add cases for other types
# (e.g., sklearn model, xgboost model, etc)
def _get_data_and_model_args(**kwargs):
    """Returns a subset of args that may correspond to data and models."""
    data_model_args = {}
    for key, value in kwargs.items():
        # Check if data or model is in the name of the key
        if "data" in key or "model" in key:
            data_model_args[key] = value
        elif isinstance(value, pd.DataFrame):
            data_model_args[key] = value

    return data_model_args


def _load(pathname: str, from_client=True) -> typing.Any:
    """Loads joblib file at pathname."""
    obj = joblib.load(pathname)
    # Set frame locals
    if from_client:
        client_frame = inspect.currentframe().f_back.f_back
        if "_mltrace_loaded_artifacts" not in client_frame.f_locals:
            client_frame.f_locals["_mltrace_loaded_artifacts"] = {}
        client_frame.f_locals["_mltrace_loaded_artifacts"].update(
            {pathname: obj}
        )

    return obj


# TODO(shreyashankar): add cases for other types
# (e.g., sklearn model, xgboost model, etc)
def _save(
    obj, pathname: str = None, var_name: str = "", from_client=True
) -> str:
    """Saves joblib object to pathname."""
    if pathname is None:
        # If being called with a component context, use the component name
        _identifier = "".join(
            random.choice(string.ascii_lowercase) for i in range(5)
        )
        pathname = (
            f'{var_name}_{_identifier}{time.strftime("%Y%m%d%H%M%S")}.mlt'
        )
        old_frame = (
            inspect.currentframe().f_back.f_back.f_back
            if from_client
            else inspect.currentframe().f_back.f_back
        )
        if "component_run" in old_frame.f_locals:
            prefix = (
                old_frame.f_locals["component_run"]
                .component_name.lower()
                .replace(" ", "_")
            )
            pathname = os.path.join(prefix, pathname)

        # Prepend with save directory
        pathname = os.path.join(
            os.environ.get(
                "SAVE_DIR", os.path.join(os.path.expanduser("~"), ".mltrace")
            ),
            pathname,
        )

    os.makedirs(os.path.dirname(pathname), exist_ok=True)
    joblib.dump(obj, pathname)

    # Set frame locals
    if from_client:
        client_frame = inspect.currentframe().f_back.f_back
        if "_mltrace_saved_artifacts" not in client_frame.f_locals:
            client_frame.f_locals["_mltrace_saved_artifacts"] = {}
        client_frame.f_locals["_mltrace_saved_artifacts"].update(
            {pathname: obj}
        )

    return pathname
