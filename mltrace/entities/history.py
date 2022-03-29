

import copy
from datetime import datetime

from mltrace.db import Store
from mltrace import utils as clientUtils


class History(object):
    def __init__(
        self,
        componentName: str,
    ):
        self.component_name = componentName
        self.store = Store(clientUtils.get_db_uri())

    def get_runs_by_time(
        self,
        start_time: datetime = datetime.min,
        end_time: datetime = datetime.max,
    ):
        history_runs = self.store.get_history(
            self.component_name, None, start_time, end_time)
        history_runs = clientUtils.convertToClient(history_runs)
        return history_runs

    def get_runs_by_index(
        self,
        front_idx: int,
        last_idx: int,
    ):
        history_runs = self.store.get_component_runs_by_index(
            self.component_name, front_idx, last_idx)
        history_runs = clientUtils.convertToClient(history_runs)
        return history_runs

    def __getitem__(self, index):
        history_run = self.store.get_component_runs_by_index(
            self.component_name, index, index + 1)
        history_run = clientUtils.convertToClient(history_run)
        return history_run

    def __len__(self):
        return self.store.get_component_runs_count(self.component_name)
