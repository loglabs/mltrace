from mltrace.db import Component, ComponentRun, IOPointer, component_run_output_association, Store

DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'
store = Store(DB_URI, delete_first=False)
session = store.Session()

sample_output = '12345'

component_run_object = session.query(ComponentRun).join(
    IOPointer, ComponentRun.outputs).filter(IOPointer.name == sample_output).first()

print(f'Printing trace for output {sample_output}...')

# Recurse!


def traverse(node, depth):
    # Print node as a step
    print(''.join(['\t' for _ in range(depth)]) + str(node))

    # Base case
    if len(node.dependencies) == 0:
        return

    # Recurse on neighbors
    for neighbor in node.dependencies:
        traverse(neighbor, depth + 1)


traverse(component_run_object, 1)
