from mltrace.db import Store
from mltrace import clean_db, create_component, register, tag_component, log_component_run, register
from mltrace.entities import ComponentRun, IOPointer

import logging
import time

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


# Clean db
clean_db()

# Create components
create_component('etl', 'generating some features', 'shreya')
tag_component('etl', ['fuck'])
create_component('training', 'training a model', 'shreya')
tag_component('training', ['fuck'])
create_component('inference', 'running a model', 'shreya')
create_component('serve', 'serving a model', 'shreya')

cr = ComponentRun('etl')
cr.add_input('raw_data.csv')
cr.add_input('cleaning_criteria.txt')
cr.add_output('features.pq')
cr.set_start_timestamp()
time.sleep(1)
cr.set_end_timestamp()
log_component_run(cr)


@register(component_name='training', inputs=['train_set.pq', 'test_set.pq'], outputs=['model.joblib', 'metrics.txt'])
def train():
    print("training model")


train()

inference_cr = ComponentRun('inference')
inference_cr.add_input('model.joblib')
inference_cr.add_input('model.joblib')
inference_cr.add_input('features.pq')
inference_cr.add_output('preds.pq')
inference_cr.set_start_timestamp()
time.sleep(1)
inference_cr.set_end_timestamp()
inference_cr.set_upstream('training')
log_component_run(inference_cr, False)


@register(component_name='serve', inputs=['preds.pq'], outputs=['serve_output_101'], endpoint=True)
def serve(x):
    print(f'serving output {x}!')


serve(x=101)
