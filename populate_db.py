# TODO(shreyashankar): handle output ids gracefully
from mltrace.db import Store
from mltrace import clean_db, create_component, register, tag_component

import logging

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


# Clean db
clean_db()

# Create components
create_component('etl', 'generating some features', 'shreya')
tag_component('etl', ['test', 'demo'])
create_component('training', 'training a model', 'shreya')
tag_component('training', ['test'])
create_component('inference', 'running a model', 'shreya')
create_component('serve', 'serving a model', 'shreya')

NUM_OUTER = 10
NUM_INNER = 10

for i in range(NUM_OUTER):
    @register('etl', inputs=[f'raw_data_{i}.pq'], outputs=[f'features_{i}.pq'])
    def etl():
        print(f'clean the data')

    @register('training', inputs=[f'train_set_{i}.pq', f'test_set_{i}.pq'], outputs=[f'model_{i}.hdf5'])
    def training():
        print(f'train a model')

    @register('inference', inputs=[f'features_{i}.pq', f'model_{i}.hdf5'], outputs=[f'preds_{i}.pq'])
    def inference():
        print(f'do model inference')

    etl()
    training()
    inference()

    for j in range(NUM_INNER):
        idx = i * NUM_OUTER + j

        @register('serve', inputs=[f'preds_{i}.pq'], outputs=[f'serve_output_{idx}'], endpoint=True)
        def serve():
            print(f'serve output')

        serve()
