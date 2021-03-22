from datetime import datetime
from mltrace.db import Store, PointerTypeEnum

import git
import logging
import time

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'
store = Store(DB_URI, delete_first=True)
repo = git.Repo(search_parent_directories=True)
sha = str(repo.head.object.hexsha)


# Create components
store.create_component('etl', 'generating some features', 'shreya')
store.create_component('training', 'training a model', 'shreya')
store.create_component('inference', 'running a model', 'shreya')
store.create_component('serve', 'serving a model', 'shreya')


for i in range(10):
    # Create component runs
    etl_component_run = store.initialize_empty_component_run('etl')
    train_component_run = store.initialize_empty_component_run('training')
    inference_component_run = store.initialize_empty_component_run('inference')
    serve_component_run = store.initialize_empty_component_run('serve')

    # Create paths
    raw_data_path = store.get_io_pointer(f'raw_data_{i}.pq')
    features_path = store.get_io_pointer(f'some_features_{i}.pq')
    train_set_path = store.get_io_pointer(f'train_set_{i}.pq')
    test_set_path = store.get_io_pointer(f'test_set_{i}.pq')
    model_path = store.get_io_pointer(f'some_model_{i}.hd5')
    predictions_path = store.get_io_pointer(f'some_preds_{i}.pq')
    logging.info(store.create_output_ids(10))
    serving_outputs = [store.get_io_pointer(
        elem, PointerTypeEnum.output_id) for elem in store.create_output_ids(10)]

    # Create params
    etl_code_snapshot = bytes(
        'def main(): print(\'Clean the fking live data\') {0}'.format(i), 'ascii')
    train_code_snapshot = bytes(
        'def main(): model.fit(train_df) {0}'.format(i), 'ascii')
    inference_code_snapshot = bytes(
        'def main(): print(\'This is inference\') {0}'.format(i), 'ascii')
    serving_code_snapshot = bytes('def main(): print(\'This is serving\') {0}'
                                  .format(i), 'ascii')

    # "Run" etl
    etl_component_run.add_input(raw_data_path)
    etl_component_run.add_output(features_path)
    etl_component_run.set_git_hash(sha)
    etl_component_run.set_code_snapshot(etl_code_snapshot)
    etl_component_run.set_start_timestamp()
    # time.sleep(2)
    etl_component_run.set_end_timestamp()
    store.commit_component_run(etl_component_run)

    # "Run" training
    train_component_run.add_inputs([train_set_path, test_set_path])
    train_component_run.add_output(model_path)
    train_component_run.set_git_hash(sha)
    train_component_run.set_code_snapshot(train_code_snapshot)
    train_component_run.set_start_timestamp()
    # time.sleep(5)
    train_component_run.set_end_timestamp()
    store.commit_component_run(train_component_run)

    # "Run" inference
    inference_component_run.add_inputs([features_path, model_path])
    inference_component_run.add_output(predictions_path)
    inference_component_run.set_git_hash(sha)
    inference_component_run.set_code_snapshot(inference_code_snapshot)
    inference_component_run.set_start_timestamp()
    # time.sleep(2)
    inference_component_run.set_end_timestamp()
    store.set_dependencies_from_inputs(inference_component_run)
    store.commit_component_run(inference_component_run)

    # "Run" serve
    serve_component_run.add_input(predictions_path)
    serve_component_run.add_outputs(serving_outputs)
    serve_component_run.set_git_hash(sha)
    serve_component_run.set_end_timestamp(serving_code_snapshot)
    serve_component_run.set_start_timestamp()
    # time.sleep(2)
    serve_component_run.set_end_timestamp()
    store.set_dependencies_from_inputs(serve_component_run)
    store.commit_component_run(serve_component_run)
