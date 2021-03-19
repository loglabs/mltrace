from mltrace.db.utils import _create_engine_wrapper, _initialize_db_tables, _drop_everything
from sqlalchemy.orm import sessionmaker


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

    def create_component(self):
        pass

    def create_empty_component_run(self):
        pass

    def create_io_pointer(self):
        pass

    def delete_component(self):
        pass

    def delete_component_run(self):
        pass

    def delete_io_pointer(self):
        pass

    def create_output_ids(self, num_outputs):
        pass

    def commit_component_run(self):
        pass

    def trace(self, output_id):
        pass

    def trace_batch(self, output_ids):
        pass
