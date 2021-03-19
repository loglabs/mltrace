from mltrace.db.utils import _create_engine_wrapper, _initialize_db_tables, _drop_everything, _traverse
from mltrace.db import Component, ComponentRun, IOPointer, PointerTypeEnum
from sqlalchemy.orm import sessionmaker

import logging
import typing


class Store(object):
    """Helper methods to interact with the db."""

    def __init__(self, uri: str, delete_first=False):
        """
        Creates the postgres database for the store. Raises exception if uri    
        isn't prefixed with postgresql://.

        Args:
            uri (str): URI string to connect to the SQLAlchemy database.
        """
        if not uri.startswith('postgresql://'):
            raise('Database URI must be prefixed with `postgresql://`')
        self.engine = _create_engine_wrapper(uri)

        # TODO(shreyashankar) remove this line
        if delete_first:
            _drop_everything(self.engine)

        # TODO(shreyashankar) check existing tables against expected tables
        _initialize_db_tables(self.engine)

        # Initialize session
        self.Session = sessionmaker(self.engine)

    def create_component(self, name: str, description: str, owner: str):
        """Creates a component entity in the database."""
        logging.info(
            f'Creating new Component with name "{name}", description "{description}", and owner "{owner}".')
        component = Component(name=name, description=description, owner=owner)
        session = self.Session()
        session.add(component)
        session.commit()
        session.close()

    def initialize_empty_component_run(self, component_name: str) -> ComponentRun:
        """Initializes an empty run for the specified component. Does not
        commit to the database."""
        component_run = ComponentRun(component_name=component_name)
        return component_run

    def get_io_pointer(self, name=str, pointer_type: PointerTypeEnum = None) -> IOPointer:
        """ Creates an io pointer around the specified path. 
        Retrieves existing io pointer if exists in DB, 
        otherwise creates a new one."""

        session = self.Session()
        res = session.query(IOPointer).filter(IOPointer.name == name).all()

        # Must create new IOPointer
        if len(res) == 0:
            logging.info(f'Creating new IOPointer with name "{name}".')
            iop = IOPointer(name=name, pointer_type=pointer_type)
            session.add(iop)
            session.commit()
            session.close()
            return iop

        # Return existing object
        session.close()
        return res[0]

    def delete_component(self):
        pass

    def delete_component_run(self):
        pass

    def delete_io_pointer(self):
        pass

    def create_output_ids(self, num_outputs=1) -> typing.List[str]:
        """Returns a list of num_outputs ids that don't already exist in the DB."""
        session = self.Session()
        res = session.query(IOPointer).filter(
            IOPointer.pointer_type == PointerTypeEnum.output_id).all()

        start_index = 0 if len(res) == 0 else max(
            res, key=lambda x: x['output_id']) + 1

        session.close()
        return [f"{i}" for i in range(start_index, start_index + num_outputs)]

    def commit_component_run(self, component_run: ComponentRun):
        """Commits a fully initialized component run to the DB."""
        status_dict = component_run.check_completeness()
        if not status_dict['success']:
            raise(status_dict['msg'])

        # Commit to DB
        session = self.Session()
        session.add(component_run)
        logging.info(
            f'Committing ComponentRun of type "{component_run.component_name}" to the database.')
        session.commit()
        session.close()

    def trace(self, output_id: str):
        """Prints trace for an output id."""
        # TODO(shreyashankar): return json instead of printing
        session = self.Session()
        component_run_object = session.query(ComponentRun).join(
            IOPointer, ComponentRun.outputs).filter(IOPointer.name == output_id).first()

        print(f'Printing trace for output {output_id}...')

        _traverse(component_run_object, 1)
        session.close()

    def trace_batch(self, output_ids: typing.List[str]):
        pass
