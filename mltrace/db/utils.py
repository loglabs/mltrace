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

import pprint
import sqlalchemy


def _create_engine_wrapper(uri: str, max_retries=5) -> sqlalchemy.engine.base.Engine:
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
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """

    con = engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for postgres (based
    # on the actual schema of the running instance)
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
    """Infers the relevnat enum for the filename."""
    data_extensions = ["csv", "pq", "parquet", "txt", "md", "rtf", "tsv", "xml", "pdf"]
    model_extensions = ["h5", "hdf5", "joblib", "pkl", "pickle", "ckpt", "mlmodel"]

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
