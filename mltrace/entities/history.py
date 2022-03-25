

import copy
from datetime import datetime

from mltrace.db import Store
from mltrace import utils as clientUtils
from mltrace.entities import ComponentRun, IOPointer


class History(object):
    def __init__(
        self,
        componentName,
    ):
        self.component_name = componentName

    def get_runs_by_time(
        self,
        start_time: datetime,
        end_time: datetime,
    ):
        store = Store(clientUtils.get_db_uri())
        history_runs = store.get_history(
            self.component_name, None, start_time, end_time)
        history_runs = History.convertToClient(history_runs)
        return history_runs

    def get_runs_by_index(
        self,
        front_idx: int,
        last_idx: int,
    ):
        store = Store(clientUtils.get_db_uri())
        history_runs = store.get_component_runs_by_index(
            self.component_name, front_idx, last_idx)
        history_runs = History.convertToClient(history_runs)
        return history_runs

    # helper function - convert to client facing component runs
    def convertToClient(componentRuns):
        component_runs = []
        for cr in componentRuns:
            inputs = [
                IOPointer.from_dictionary(iop.__dict__).to_dictionary()
                for iop in cr.inputs
            ]
            outputs = [
                IOPointer.from_dictionary(iop.__dict__).to_dictionary()
                for iop in cr.outputs
            ]
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

    def __getitem__(self, index):
        store = Store(clientUtils.get_db_uri())
        history_run = store.get_component_runs_by_index(
            self.component_name, index, index + 1)
        history_run = History.convertToClient(history_run)
        return history_run

    def __len__(self):
        store = Store(clientUtils.get_db_uri())
        return store.get_component_runs_count(self.component_name)
