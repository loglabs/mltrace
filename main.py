from mltrace.entities import Component, ComponentRun

import time

c = Component('fakename', 'fakedesc', 'shreya')

cr = ComponentRun(c.name, None, None, None, None, None, None, None)
cr.set_start_timestamp()
time.sleep(10)
cr.set_end_timestamp()

for k, v in cr:
    print(k, v)
