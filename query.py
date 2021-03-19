from mltrace.db.base import Session
from mltrace.db.models import Component, ComponentRun, IOPointer, component_run_output_association


output = '12345'
session = Session()

component_run_object = session.query(ComponentRun).join(
    IOPointer, ComponentRun.outputs).filter(IOPointer.name == output).first()

print(f'Printing trace for output {output}...')

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
