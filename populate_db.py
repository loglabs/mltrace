from datetime import datetime
from mltrace.db import Store

import logging
import time

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'
store = Store(DB_URI, delete_first=True)


# Create components
store.create_component('etl', 'generating some features', 'shreya')
store.create_component('training', 'training a model', 'shreya')
store.create_component('inference', 'running a model', 'shreya')
store.create_component('serve', 'serving a model', 'shreya')

# Create component runs
etl_component_run = store.initialize_empty_component_run('etl')
train_component_run = store.initialize_empty_component_run('training')
inference_component_run = store.initialize_empty_component_run('inference')
serve_component_run = store.initialize_empty_component_run('serve')

# Create paths
raw_data_path = store.get_io_pointer('raw_data.pq')
features_path = store.get_io_pointer('some_features.pq')
train_set_path = store.get_io_pointer('train_set.pq')
test_set_path = store.get_io_pointer('test_set.pq')
model_path = store.get_io_pointer('some_model.hd5')
predictions_path = store.get_io_pointer('some_preds.pq')
serving_output = store.get_io_pointer('asdlfasdf')

# Create params
etl_code_snapshot = b'def main(): print(\'Clean the fucking live data\')'
train_code_snapshot = b'def main(): model.fit(train_df)'
inference_code_snapshot = b'def main(): print(\'This is inference\')'
serving_code_snapshot = b'def main(): print(\'This is serving\')'

# "Run" etl
etl_component_run.add_input(raw_data_path)
etl_component_run.add_output(features_path)
etl_component_run.set_code_snapshot(etl_code_snapshot)
etl_component_run.set_start_timestamp()
time.sleep(2)
etl_component_run.set_end_timestamp()
store.commit_component_run(etl_component_run)

# "Run" training
train_component_run.add_inputs([train_set_path, test_set_path])
train_component_run.add_output(model_path)
train_component_run.set_code_snapshot(train_code_snapshot)
train_component_run.set_start_timestamp()
time.sleep(5)
train_component_run.set_end_timestamp()
store.commit_component_run(train_component_run)

# "Run" inference
inference_component_run.add_inputs([features_path, model_path])
inference_component_run.add_output(predictions_path)
inference_component_run.set_code_snapshot(inference_code_snapshot)
inference_component_run.set_start_timestamp()
time.sleep(2)
inference_component_run.set_end_timestamp()
store.set_dependencies_from_inputs(inference_component_run, 'some_features.pq')
store.set_dependencies_from_inputs(inference_component_run, 'some_model.hd5')
store.commit_component_run(inference_component_run)

# "Run" serve
serve_component_run.add_input(predictions_path)
serve_component_run.add_output(serving_output)
serve_component_run.set_end_timestamp(serving_code_snapshot)
serve_component_run.set_start_timestamp()
time.sleep(2)
serve_component_run.set_end_timestamp()
store.set_dependencies_from_inputs(serve_component_run, 'some_preds.pq')
store.commit_component_run(serve_component_run)
