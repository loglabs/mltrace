from datetime import datetime
from mltrace.db.base import Session, engine, Base
from mltrace.db.models import Component, ComponentRun, IOPointer
from mltrace.db.utils import drop_everything

import time

# Generate database schema and new session
drop_everything(engine)
Base.metadata.create_all(engine)
session = Session()


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
etl_component_run.inputs = [raw_data_path]
etl_component_run.outputs = [features_path]
etl_component_run.code_snapshot = etl_code_snapshot
etl_component_run.start_time = datetime.now()
time.sleep(2)
etl_component_run.end_time = datetime.now()

# "Run" training
train_component_run.inputs = [train_set_path, test_set_path]
train_component_run.outputs = [model_path]
train_component_run.code_snapshot = train_code_snapshot
train_component_run.start_time = datetime.now()
time.sleep(5)
train_component_run.end_time = datetime.now()

# "Run" inference
inference_component_run.inputs = [features_path, model_path]
inference_component_run.outputs = [predictions_path]
inference_component_run.code_snapshot = inference_code_snapshot
inference_component_run.start_time = datetime.now()
time.sleep(2)
inference_component_run.end_time = datetime.now()
inference_component_run.dependencies = [etl_component_run, train_component_run]

# "Run" serve
serve_component_run.inputs = [predictions_path]
serve_component_run.outputs = [serving_output]
serve_component_run.code_snapshot = serving_code_snapshot
serve_component_run.start_time = datetime.now()
time.sleep(2)
serve_component_run.end_time = datetime.now()
serve_component_run.dependencies = [inference_component_run]

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
