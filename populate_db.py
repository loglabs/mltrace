from datetime import datetime
from mltrace.db import Component, ComponentRun, IOPointer, Store

import time

DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'
store = Store(DB_URI, delete_first=True)
session = store.Session()


# Create components
etl_component = Component('etl', 'generating some features', 'shreya')
train_component = Component('training', 'training a model', 'shreya')
inference_component = Component('inference', 'running a model', 'shreya')
serve_component = Component('serve', 'serving a model', 'shreya')

# Create component runs
etl_component_run = ComponentRun('etl')
train_component_run = ComponentRun('training')
inference_component_run = ComponentRun('inference')
serve_component_run = ComponentRun('serve')

# Create paths
raw_data_path = IOPointer('raw_data.pq')
features_path = IOPointer('some_features.pq')
train_set_path = IOPointer('train_set.pq')
test_set_path = IOPointer('test_set.pq')
model_path = IOPointer('some_model.hd5')
predictions_path = IOPointer('some_preds.pq')
serving_output = IOPointer('12345')

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

# "Run" training
train_component_run.add_inputs([train_set_path, test_set_path])
train_component_run.add_output(model_path)
train_component_run.set_code_snapshot(train_code_snapshot)
train_component_run.set_start_timestamp()
time.sleep(5)
train_component_run.set_end_timestamp()

# "Run" inference
inference_component_run.add_inputs([features_path, model_path])
inference_component_run.add_output(predictions_path)
inference_component_run.set_code_snapshot(inference_code_snapshot)
inference_component_run.set_start_timestamp()
time.sleep(2)
inference_component_run.set_end_timestamp()
inference_component_run.set_upstream([etl_component_run, train_component_run])

# "Run" serve
serve_component_run.add_input(predictions_path)
serve_component_run.add_output(serving_output)
serve_component_run.set_end_timestamp(serving_code_snapshot)
serve_component_run.set_start_timestamp()
time.sleep(2)
serve_component_run.set_end_timestamp()
serve_component_run.set_upstream(inference_component_run)

# Add to session
session.add(etl_component)
session.add(train_component)
session.add(inference_component)
session.add(serve_component)
session.add(etl_component_run)
session.add(train_component_run)
session.add(inference_component_run)
session.add(serve_component_run)

# Commit and close session
session.commit()
session.close()
