# from mltrace.entities import Component, ComponentRun

# import time

# c = Component('fakename', 'fakedesc', 'shreya')

# cr = ComponentRun(c.name, None, None, None, None, None, None, None)
# cr.set_start_timestamp()
# time.sleep(10)
# cr.set_end_timestamp()

# for k, v in cr:
#     print(k, v)

from datetime import datetime

from mltrace.db.base import Session, engine, Base
from mltrace.db.models import Component, ComponentRun, IOPointer
from mltrace.db.utils import drop_everything

# Generate database schema and new session
drop_everything(engine)
Base.metadata.create_all(engine)
session = Session()


# Create components
inference_component = Component('inference', 'running a model', 'shreya')
serve_component = Component('serve', 'serving a model', 'shreya')

# Create component runs
inference_component_run = ComponentRun('inference')
serve_component_run = ComponentRun('serve')

# Create paths
features_path = IOPointer('some_features.pq')
model_path = IOPointer('some_model.hd5')
predictions_path = IOPointer('some_preds.pq')
serving_output = IOPointer('some_id_of_choice')

# Create params
inference_code_snapshot = b'def main(): print(\'This is inference\')'
serving_code_snapshot = b'def main(): print(\'This is inference\')'

# "Run" inference
inference_component_run.inputs = [features_path, model_path]
inference_component_run.outputs = [predictions_path]
inference_component_run.code_snapshot = inference_code_snapshot

# Add to session
session.add(inference_component)
session.add(serve_component)
session.add(inference_component_run)
session.add(serve_component_run)


# Commit and close session
session.commit()
session.close()
