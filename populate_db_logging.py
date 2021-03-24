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

cr = ComponentRun(component_name='etl')
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

cr = ComponentRun(component_name='inference')
cr.add_input('model.joblib')
cr.add_input('features.pq')
cr.add_output('preds.pq')
cr.set_start_timestamp()
time.sleep(1)
cr.set_end_timestamp()
log_component_run(cr)


@register(component_name='serve', inputs=['preds.pq'], outputs=['serve_output_101'], endpoint=True)
def serve():
    print('serving output 101!')


serve()
