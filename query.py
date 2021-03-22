from mltrace.db import Component, ComponentRun, IOPointer, Store

import logging

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

DB_URI = 'postgresql://usr:pass@localhost:5432/sqlalchemy'
store = Store(DB_URI, delete_first=False)

while(True):
    inp = input(
        'Input output id you want to trace or press enter to quit. ').strip()
    if inp == '':
        exit(0)
    try:
        store.trace(inp)
    except:
        print(f'{inp} not recognized. Please try again.')
        continue
