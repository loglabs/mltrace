

from datetime import datetime

from mltrace.db import Store
from mltrace import utils as clientUtils


class History(object):
    def __init__(
        self,
        componentName,
    ):
        # {component_run_id: component_run} sort by time
        self.component_name = componentName

        # should I choose a ordered orderDict / list ?
        # self.history_component_runs = {}
        
    def get_runs_by_time(
        self,
        start_time: datetime,
        end_time: datetime,
    ):
        store = Store(clientUtils.get_db_uri())
        history_runs = store.get_history(self.component_name, None, start_time, end_time)
        # TODO: Client.py - convert to client facing component run object
        return str(history_runs)

    def get_runs_by_index(
        self,
        front_idx: int,
        last_idx: int,
    ):
        store = Store(clientUtils.get_db_uri())
        history_runs = store.get_component_runs_by_index(self.component_name, front_idx, last_idx)
        return str(history_runs)

    # all lazy loading functions

    def __getitem__(self, index):
        store = Store(clientUtils.get_db_uri())
        history_run = store.get_component_runs_by_index(self.component_name, index, index + 1)
        return str(history_run)

    def __len__(self):
        store = Store(clientUtils.get_db_uri())
        return store.get_component_runs_count(self.component_name)